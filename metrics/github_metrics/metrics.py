"""
Metrics calculation module for GitHub repository analysis.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class DORAMetrics:
    """Calculate DORA (DevOps Research and Assessment) metrics."""
    
    def __init__(self, data: Dict[str, List[Dict[str, Any]]]):
        """
        Initialize with collected GitHub data.
        
        Args:
            data: Dictionary containing 'deployments', 'pull_requests', and 'issues' data
        """
        self.deployments = pd.DataFrame(data.get('deployments', []))
        self.pull_requests = pd.DataFrame(data.get('pull_requests', []))
        self.issues = pd.DataFrame(data.get('issues', []))
        
        # Convert datetime columns
        self._convert_datetime_columns()
    
    def _convert_datetime_columns(self):
        """Convert datetime columns to proper datetime types."""
        datetime_cols = ['created_at', 'updated_at', 'closed_at', 'merged_at']
        
        for df in [self.deployments, self.pull_requests, self.issues]:
            if not df.empty:
                for col in datetime_cols:
                    if col in df.columns:
                        df[col] = pd.to_datetime(df[col])
    
    def deployment_frequency(self, period_days: int = 30) -> Dict[str, Any]:
        """
        Calculate deployment frequency.
        
        Args:
            period_days: Period to calculate frequency over
            
        Returns:
            Dictionary with frequency metrics
        """
        if self.deployments.empty:
            return {
                "deployments_per_day": 0,
                "deployments_per_week": 0,
                "total_deployments": 0,
                "period_days": period_days
            }
        
        # Filter deployments within the period
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days)
        
        period_deployments = self.deployments[
            (self.deployments['created_at'] >= start_date) &
            (self.deployments['created_at'] <= end_date)
        ]
        
        total_deployments = len(period_deployments)
        deployments_per_day = total_deployments / period_days if period_days > 0 else 0
        deployments_per_week = deployments_per_day * 7
        
        return {
            "deployments_per_day": round(deployments_per_day, 2),
            "deployments_per_week": round(deployments_per_week, 2),
            "total_deployments": total_deployments,
            "period_days": period_days
        }
    
    def lead_time_for_changes(self) -> Dict[str, Any]:
        """
        Calculate lead time for changes (time from commit to production).
        Using PR merge time as proxy for lead time.
        
        Returns:
            Dictionary with lead time metrics
        """
        if self.pull_requests.empty:
            return {
                "mean_lead_time_hours": 0,
                "median_lead_time_hours": 0,
                "p95_lead_time_hours": 0,
                "total_merged_prs": 0
            }
        
        # Filter merged PRs with valid cycle times
        merged_prs = self.pull_requests[
            (self.pull_requests['merged'] == True) &
            (self.pull_requests['cycle_time_hours'].notna())
        ]
        
        if merged_prs.empty:
            return {
                "mean_lead_time_hours": 0,
                "median_lead_time_hours": 0,
                "p95_lead_time_hours": 0,
                "total_merged_prs": 0
            }
        
        lead_times = merged_prs['cycle_time_hours']
        
        return {
            "mean_lead_time_hours": round(lead_times.mean(), 2),
            "median_lead_time_hours": round(lead_times.median(), 2),
            "p95_lead_time_hours": round(lead_times.quantile(0.95), 2),
            "total_merged_prs": len(merged_prs)
        }
    
    def mean_time_to_recovery(self) -> Dict[str, Any]:
        """
        Calculate mean time to recovery from incidents.
        Using bug/incident issues as proxy.
        
        Returns:
            Dictionary with recovery time metrics
        """
        if self.issues.empty:
            return {
                "mean_recovery_time_hours": 0,
                "median_recovery_time_hours": 0,
                "total_incidents": 0
            }
        
        # Filter closed incident/bug issues
        incidents = self.issues[
            (self.issues['state'] == 'closed') &
            ((self.issues['is_bug'] == True) | (self.issues['is_incident'] == True)) &
            (self.issues['created_at'].notna()) &
            (self.issues['closed_at'].notna())
        ]
        
        if incidents.empty:
            return {
                "mean_recovery_time_hours": 0,
                "median_recovery_time_hours": 0,
                "total_incidents": 0
            }
        
        # Calculate recovery times
        recovery_times = (
            incidents['closed_at'] - incidents['created_at']
        ).dt.total_seconds() / 3600  # Convert to hours
        
        return {
            "mean_recovery_time_hours": round(recovery_times.mean(), 2),
            "median_recovery_time_hours": round(recovery_times.median(), 2),
            "total_incidents": len(incidents)
        }
    
    def change_failure_rate(self, period_days: int = 30) -> Dict[str, Any]:
        """
        Calculate change failure rate.
        Using ratio of bug issues to deployments as proxy.
        
        Args:
            period_days: Period to calculate rate over
            
        Returns:
            Dictionary with failure rate metrics
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days)
        
        # Count deployments in period
        if not self.deployments.empty:
            period_deployments = self.deployments[
                (self.deployments['created_at'] >= start_date) &
                (self.deployments['created_at'] <= end_date)
            ]
            total_deployments = len(period_deployments)
        else:
            total_deployments = 0
        
        # Count bug issues created in period
        if not self.issues.empty:
            period_bugs = self.issues[
                (self.issues['created_at'] >= start_date) &
                (self.issues['created_at'] <= end_date) &
                (self.issues['is_bug'] == True)
            ]
            total_bugs = len(period_bugs)
        else:
            total_bugs = 0
        
        # Calculate failure rate
        if total_deployments > 0:
            failure_rate = total_bugs / total_deployments
        else:
            failure_rate = 0
        
        return {
            "change_failure_rate": round(failure_rate, 3),
            "total_deployments": total_deployments,
            "total_bugs": total_bugs,
            "period_days": period_days
        }
    
    def get_all_dora_metrics(self, period_days: int = 30) -> Dict[str, Any]:
        """Get all DORA metrics in one call."""
        return {
            "deployment_frequency": self.deployment_frequency(period_days),
            "lead_time_for_changes": self.lead_time_for_changes(),
            "mean_time_to_recovery": self.mean_time_to_recovery(),
            "change_failure_rate": self.change_failure_rate(period_days),
            "calculated_at": datetime.now().isoformat(),
            "period_days": period_days
        }


class PRMetrics:
    """Calculate Pull Request related metrics."""
    
    def __init__(self, pull_requests: List[Dict[str, Any]]):
        """Initialize with pull request data."""
        self.prs = pd.DataFrame(pull_requests)
        if not self.prs.empty:
            self._convert_datetime_columns()
    
    def _convert_datetime_columns(self):
        """Convert datetime columns."""
        datetime_cols = ['created_at', 'updated_at', 'closed_at', 'merged_at']
        for col in datetime_cols:
            if col in self.prs.columns:
                self.prs[col] = pd.to_datetime(self.prs[col])
    
    def cycle_time_analysis(self) -> Dict[str, Any]:
        """Analyze PR cycle times."""
        if self.prs.empty:
            return {"error": "No PR data available"}
        
        # Filter PRs with valid cycle times
        valid_prs = self.prs[self.prs['cycle_time_hours'].notna()]
        
        if valid_prs.empty:
            return {"error": "No PRs with valid cycle times"}
        
        cycle_times = valid_prs['cycle_time_hours']
        
        return {
            "mean_cycle_time_hours": round(cycle_times.mean(), 2),
            "median_cycle_time_hours": round(cycle_times.median(), 2),
            "p75_cycle_time_hours": round(cycle_times.quantile(0.75), 2),
            "p95_cycle_time_hours": round(cycle_times.quantile(0.95), 2),
            "min_cycle_time_hours": round(cycle_times.min(), 2),
            "max_cycle_time_hours": round(cycle_times.max(), 2),
            "total_prs": len(valid_prs)
        }
    
    def review_analysis(self) -> Dict[str, Any]:
        """Analyze code review metrics."""
        if self.prs.empty:
            return {"error": "No PR data available"}
        
        # Review comments analysis
        review_comments = self.prs['review_comments']
        total_comments = self.prs['total_comments']
        
        # PR size analysis
        pr_sizes = self.prs['additions'] + self.prs['deletions']
        
        return {
            "mean_review_comments": round(review_comments.mean(), 2),
            "median_review_comments": round(review_comments.median(), 2),
            "mean_total_comments": round(total_comments.mean(), 2),
            "median_total_comments": round(total_comments.median(), 2),
            "mean_pr_size": round(pr_sizes.mean(), 2),
            "median_pr_size": round(pr_sizes.median(), 2),
            "prs_with_no_reviews": len(self.prs[self.prs['review_comments'] == 0]),
            "total_prs": len(self.prs)
        }
    
    def merge_analysis(self) -> Dict[str, Any]:
        """Analyze merge patterns."""
        if self.prs.empty:
            return {"error": "No PR data available"}
        
        total_prs = len(self.prs)
        merged_prs = len(self.prs[self.prs['merged'] == True])
        closed_unmerged = len(self.prs[
            (self.prs['state'] == 'closed') & (self.prs['merged'] == False)
        ])
        open_prs = len(self.prs[self.prs['state'] == 'open'])
        
        return {
            "total_prs": total_prs,
            "merged_prs": merged_prs,
            "closed_unmerged_prs": closed_unmerged,
            "open_prs": open_prs,
            "merge_rate": round(merged_prs / total_prs, 3) if total_prs > 0 else 0,
            "rejection_rate": round(closed_unmerged / total_prs, 3) if total_prs > 0 else 0
        }


class ProductivityMetrics:
    """Calculate developer productivity metrics."""
    
    def __init__(self, data: Dict[str, List[Dict[str, Any]]]):
        """Initialize with GitHub data."""
        self.commits = pd.DataFrame(data.get('commits', []))
        self.pull_requests = pd.DataFrame(data.get('pull_requests', []))
        
        if not self.commits.empty:
            self._convert_commit_datetime()
        if not self.pull_requests.empty:
            self._convert_pr_datetime()
    
    def _convert_commit_datetime(self):
        """Convert commit datetime columns."""
        if 'date' in self.commits.columns:
            self.commits['date'] = pd.to_datetime(self.commits['date'])
    
    def _convert_pr_datetime(self):
        """Convert PR datetime columns."""
        datetime_cols = ['created_at', 'updated_at', 'closed_at', 'merged_at']
        for col in datetime_cols:
            if col in self.pull_requests.columns:
                self.pull_requests[col] = pd.to_datetime(self.pull_requests[col])
    
    def developer_activity(self, period_days: int = 30) -> Dict[str, Any]:
        """Analyze developer activity metrics."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days)
        
        metrics = {}
        
        # Commit analysis
        if not self.commits.empty:
            period_commits = self.commits[
                (self.commits['date'] >= start_date) &
                (self.commits['date'] <= end_date)
            ]
            
            # Group by author
            author_stats = period_commits.groupby('author').agg({
                'sha': 'count',
                'additions': 'sum',
                'deletions': 'sum',
                'total_changes': 'sum',
                'files_changed': 'sum'
            }).rename(columns={'sha': 'commits'})
            
            metrics['commit_activity'] = {
                "total_commits": len(period_commits),
                "total_authors": len(author_stats),
                "mean_commits_per_author": round(author_stats['commits'].mean(), 2),
                "mean_changes_per_commit": round(period_commits['total_changes'].mean(), 2),
                "top_contributors": author_stats.head(5).to_dict('index')
            }
        
        # PR analysis
        if not self.pull_requests.empty:
            period_prs = self.pull_requests[
                (self.pull_requests['created_at'] >= start_date) &
                (self.pull_requests['created_at'] <= end_date)
            ]
            
            pr_author_stats = period_prs.groupby('author').agg({
                'number': 'count',
                'additions': 'sum',
                'deletions': 'sum',
                'review_comments': 'sum'
            }).rename(columns={'number': 'prs'})
            
            metrics['pr_activity'] = {
                "total_prs": len(period_prs),
                "pr_authors": len(pr_author_stats),
                "mean_prs_per_author": round(pr_author_stats['prs'].mean(), 2),
                "mean_pr_size": round((period_prs['additions'] + period_prs['deletions']).mean(), 2),
                "top_pr_contributors": pr_author_stats.head(5).to_dict('index')
            }
        
        metrics['period_days'] = period_days
        metrics['calculated_at'] = datetime.now().isoformat()
        
        return metrics
    
    def code_quality_trends(self) -> Dict[str, Any]:
        """Analyze code quality trends based on PR metrics."""
        if self.pull_requests.empty:
            return {"error": "No PR data available"}
        
        # Group by week to see trends
        self.pull_requests['week'] = self.pull_requests['created_at'].dt.isocalendar().week
        
        weekly_stats = self.pull_requests.groupby('week').agg({
            'review_comments': 'mean',
            'total_comments': 'mean',
            'cycle_time_hours': 'mean',
            'additions': 'mean',
            'deletions': 'mean',
            'changed_files': 'mean'
        })
        
        return {
            "weekly_trends": weekly_stats.to_dict('index'),
            "overall_averages": {
                "avg_review_comments": round(self.pull_requests['review_comments'].mean(), 2),
                "avg_cycle_time": round(self.pull_requests['cycle_time_hours'].mean(), 2),
                "avg_pr_size": round((self.pull_requests['additions'] + self.pull_requests['deletions']).mean(), 2)
            }
        }
    
    def collaboration_metrics(self) -> Dict[str, Any]:
        """Analyze collaboration patterns."""
        if self.pull_requests.empty:
            return {"error": "No PR data available"}
        
        # Reviewer analysis
        all_reviewers = []
        for reviewers in self.pull_requests['reviewers']:
            if isinstance(reviewers, list):
                all_reviewers.extend(reviewers)
        
        reviewer_counts = pd.Series(all_reviewers).value_counts()
        
        # Cross-team collaboration (based on different authors and reviewers)
        collaboration_pairs = []
        for _, pr in self.pull_requests.iterrows():
            author = pr['author']
            reviewers = pr['reviewers'] if isinstance(pr['reviewers'], list) else []
            for reviewer in reviewers:
                if reviewer != author:
                    collaboration_pairs.append((author, reviewer))
        
        return {
            "total_reviewers": len(reviewer_counts),
            "most_active_reviewers": reviewer_counts.head(5).to_dict(),
            "collaboration_pairs": len(set(collaboration_pairs)),
            "avg_reviewers_per_pr": round(
                self.pull_requests['reviewers'].apply(
                    lambda x: len(x) if isinstance(x, list) else 0
                ).mean(), 2
            )
        }
