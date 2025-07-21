"""
Utility functions for GitHub metrics collection and analysis.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json
import os

logger = logging.getLogger(__name__)


def setup_logging(level: str = "INFO"):
    """Setup logging configuration."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('github_metrics.log')
        ]
    )


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safely divide two numbers, returning default if denominator is zero."""
    if denominator == 0:
        return default
    return numerator / denominator


def format_duration(hours: float) -> str:
    """Format duration in hours to human-readable string."""
    if hours < 1:
        return f"{hours * 60:.0f} minutes"
    elif hours < 24:
        return f"{hours:.1f} hours"
    else:
        days = hours / 24
        return f"{days:.1f} days"


def calculate_percentile_range(data: List[float], percentiles: List[float]) -> Dict[str, float]:
    """Calculate multiple percentiles for a dataset."""
    import numpy as np
    
    if not data:
        return {f"p{int(p*100)}": 0.0 for p in percentiles}
    
    return {
        f"p{int(p*100)}": float(np.percentile(data, p * 100))
        for p in percentiles
    }


def get_business_hours_between(start: datetime, end: datetime) -> float:
    """
    Calculate business hours between two datetime objects.
    Assumes 8-hour business days, Monday-Friday.
    """
    if start >= end:
        return 0.0
    
    current = start
    business_hours = 0.0
    
    while current.date() <= end.date():
        # Skip weekends
        if current.weekday() >= 5:  # Saturday = 5, Sunday = 6
            current += timedelta(days=1)
            current = current.replace(hour=9, minute=0, second=0, microsecond=0)
            continue
        
        # Business day start and end
        day_start = current.replace(hour=9, minute=0, second=0, microsecond=0)
        day_end = current.replace(hour=17, minute=0, second=0, microsecond=0)
        
        # Adjust for actual start/end times
        if current.date() == start.date():
            day_start = max(start, day_start)
        if current.date() == end.date():
            day_end = min(end, day_end)
        
        if day_start < day_end:
            business_hours += (day_end - day_start).total_seconds() / 3600
        
        current += timedelta(days=1)
        current = current.replace(hour=9, minute=0, second=0, microsecond=0)
    
    return business_hours


def detect_outliers(data: List[float], method: str = "iqr") -> Dict[str, Any]:
    """
    Detect outliers in a dataset using specified method.
    
    Args:
        data: List of numeric values
        method: Detection method ("iqr" or "zscore")
        
    Returns:
        Dictionary with outlier analysis
    """
    import numpy as np
    
    if not data or len(data) < 4:
        return {"outliers": [], "clean_data": data, "method": method}
    
    data_array = np.array(data)
    
    if method == "iqr":
        q1 = np.percentile(data_array, 25)
        q3 = np.percentile(data_array, 75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        outliers = data_array[(data_array < lower_bound) | (data_array > upper_bound)]
        clean_data = data_array[(data_array >= lower_bound) & (data_array <= upper_bound)]
        
    elif method == "zscore":
        mean = np.mean(data_array)
        std = np.std(data_array)
        z_scores = np.abs((data_array - mean) / std)
        
        outliers = data_array[z_scores > 2]  # 2 standard deviations
        clean_data = data_array[z_scores <= 2]
    
    else:
        raise ValueError(f"Unknown outlier detection method: {method}")
    
    return {
        "outliers": outliers.tolist(),
        "clean_data": clean_data.tolist(),
        "outlier_count": len(outliers),
        "outlier_percentage": len(outliers) / len(data) * 100,
        "method": method
    }


def create_time_series_data(
    data: List[Dict[str, Any]],
    date_field: str,
    value_field: str,
    aggregation: str = "count",
    period: str = "day"
) -> Dict[str, List]:
    """
    Create time series data from a list of records.
    
    Args:
        data: List of data records
        date_field: Field name containing datetime
        value_field: Field name containing values to aggregate
        aggregation: Aggregation method ("count", "sum", "mean")
        period: Time period for grouping ("day", "week", "month")
        
    Returns:
        Dictionary with dates and values lists
    """
    import pandas as pd
    
    if not data:
        return {"dates": [], "values": []}
    
    df = pd.DataFrame(data)
    
    if date_field not in df.columns:
        return {"dates": [], "values": []}
    
    # Convert to datetime
    df[date_field] = pd.to_datetime(df[date_field])
    
    # Group by period
    if period == "day":
        df['period'] = df[date_field].dt.date
    elif period == "week":
        df['period'] = df[date_field].dt.to_period('W').dt.start_time.dt.date
    elif period == "month":
        df['period'] = df[date_field].dt.to_period('M').dt.start_time.dt.date
    else:
        raise ValueError(f"Unknown period: {period}")
    
    # Aggregate
    if aggregation == "count":
        grouped = df.groupby('period').size()
    elif aggregation == "sum":
        grouped = df.groupby('period')[value_field].sum()
    elif aggregation == "mean":
        grouped = df.groupby('period')[value_field].mean()
    else:
        raise ValueError(f"Unknown aggregation: {aggregation}")
    
    return {
        "dates": [str(date) for date in grouped.index],
        "values": grouped.values.tolist()
    }


def save_metrics_to_file(metrics: Dict[str, Any], filepath: str):
    """Save metrics to JSON file with proper formatting."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    with open(filepath, 'w') as f:
        json.dump(metrics, f, indent=2, default=str)
    
    logger.info(f"Metrics saved to {filepath}")


def load_metrics_from_file(filepath: str) -> Optional[Dict[str, Any]]:
    """Load metrics from JSON file."""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning(f"Metrics file not found: {filepath}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse metrics file {filepath}: {e}")
        return None


def compare_metrics(current: Dict[str, Any], previous: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compare current metrics with previous period to show trends.
    
    Args:
        current: Current period metrics
        previous: Previous period metrics
        
    Returns:
        Dictionary with comparison results
    """
    comparison = {}
    
    # DORA metrics comparison
    if 'dora_metrics' in current and 'dora_metrics' in previous:
        dora_current = current['dora_metrics']
        dora_previous = previous['dora_metrics']
        
        comparison['dora_trends'] = {}
        
        # Deployment frequency
        if 'deployment_frequency' in dora_current and 'deployment_frequency' in dora_previous:
            current_freq = dora_current['deployment_frequency'].get('deployments_per_week', 0)
            previous_freq = dora_previous['deployment_frequency'].get('deployments_per_week', 0)
            
            comparison['dora_trends']['deployment_frequency'] = {
                'current': current_freq,
                'previous': previous_freq,
                'change': current_freq - previous_freq,
                'change_percent': safe_divide(
                    (current_freq - previous_freq), previous_freq, 0
                ) * 100
            }
        
        # Lead time
        if 'lead_time_for_changes' in dora_current and 'lead_time_for_changes' in dora_previous:
            current_lead = dora_current['lead_time_for_changes'].get('median_lead_time_hours', 0)
            previous_lead = dora_previous['lead_time_for_changes'].get('median_lead_time_hours', 0)
            
            comparison['dora_trends']['lead_time'] = {
                'current': current_lead,
                'previous': previous_lead,
                'change': current_lead - previous_lead,
                'change_percent': safe_divide(
                    (current_lead - previous_lead), previous_lead, 0
                ) * 100
            }
    
    # PR metrics comparison
    if 'pr_metrics' in current and 'pr_metrics' in previous:
        pr_current = current['pr_metrics']
        pr_previous = previous['pr_metrics']
        
        comparison['pr_trends'] = {}
        
        # Cycle time
        cycle_current = pr_current.get('cycle_time_analysis', {})
        cycle_previous = pr_previous.get('cycle_time_analysis', {})
        
        if 'mean_cycle_time_hours' in cycle_current and 'mean_cycle_time_hours' in cycle_previous:
            current_cycle = cycle_current['mean_cycle_time_hours']
            previous_cycle = cycle_previous['mean_cycle_time_hours']
            
            comparison['pr_trends']['cycle_time'] = {
                'current': current_cycle,
                'previous': previous_cycle,
                'change': current_cycle - previous_cycle,
                'change_percent': safe_divide(
                    (current_cycle - previous_cycle), previous_cycle, 0
                ) * 100
            }
    
    comparison['calculated_at'] = datetime.now().isoformat()
    
    return comparison


def generate_summary_report(metrics: Dict[str, Any]) -> str:
    """Generate a human-readable summary report of metrics."""
    report_lines = []
    
    report_lines.append("# GitHub Metrics Summary Report")
    report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("")
    
    # DORA Metrics
    if 'dora_metrics' in metrics:
        dora = metrics['dora_metrics']
        report_lines.append("## DORA Metrics")
        
        if 'deployment_frequency' in dora:
            freq = dora['deployment_frequency']
            report_lines.append(f"- **Deployment Frequency**: {freq.get('deployments_per_week', 0):.2f} per week")
        
        if 'lead_time_for_changes' in dora:
            lead_time = dora['lead_time_for_changes']
            median_hours = lead_time.get('median_lead_time_hours', 0)
            report_lines.append(f"- **Lead Time**: {format_duration(median_hours)} (median)")
        
        if 'mean_time_to_recovery' in dora:
            mttr = dora['mean_time_to_recovery']
            recovery_hours = mttr.get('mean_recovery_time_hours', 0)
            report_lines.append(f"- **MTTR**: {format_duration(recovery_hours)} (mean)")
        
        if 'change_failure_rate' in dora:
            cfr = dora['change_failure_rate']
            failure_rate = cfr.get('change_failure_rate', 0)
            report_lines.append(f"- **Change Failure Rate**: {failure_rate:.1%}")
        
        report_lines.append("")
    
    # PR Metrics
    if 'pr_metrics' in metrics:
        pr_metrics = metrics['pr_metrics']
        report_lines.append("## Pull Request Metrics")
        
        if 'cycle_time_analysis' in pr_metrics:
            cycle = pr_metrics['cycle_time_analysis']
            if 'error' not in cycle:
                mean_hours = cycle.get('mean_cycle_time_hours', 0)
                report_lines.append(f"- **Average PR Cycle Time**: {format_duration(mean_hours)}")
                report_lines.append(f"- **Total PRs Analyzed**: {cycle.get('total_prs', 0)}")
        
        if 'review_analysis' in pr_metrics:
            review = pr_metrics['review_analysis']
            if 'error' not in review:
                avg_comments = review.get('mean_review_comments', 0)
                report_lines.append(f"- **Average Review Comments**: {avg_comments:.1f}")
        
        if 'merge_analysis' in pr_metrics:
            merge = pr_metrics['merge_analysis']
            if 'error' not in merge:
                merge_rate = merge.get('merge_rate', 0)
                report_lines.append(f"- **PR Merge Rate**: {merge_rate:.1%}")
        
        report_lines.append("")
    
    # Productivity Metrics
    if 'productivity_metrics' in metrics:
        productivity = metrics['productivity_metrics']
        report_lines.append("## Productivity Metrics")
        
        if 'developer_activity' in productivity:
            activity = productivity['developer_activity']
            
            if 'commit_activity' in activity:
                commits = activity['commit_activity']
                report_lines.append(f"- **Total Commits**: {commits.get('total_commits', 0)}")
                report_lines.append(f"- **Active Contributors**: {commits.get('total_authors', 0)}")
            
            if 'pr_activity' in activity:
                pr_activity = activity['pr_activity']
                report_lines.append(f"- **Total PRs**: {pr_activity.get('total_prs', 0)}")
    
    return "\n".join(report_lines)
