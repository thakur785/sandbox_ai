"""
Airflow DAG for collecting GitHub metrics and calculating DORA metrics.
"""

from datetime import datetime, timedelta
import logging
import json
import os
from typing import Dict, Any

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable
from airflow.utils.dates import days_ago

# Import our custom modules
import sys
sys.path.append('/opt/airflow/dags/github_metrics')

from collectors import GitHubCollector
from metrics import DORAMetrics, PRMetrics, ProductivityMetrics
from dashboard import create_static_charts

logger = logging.getLogger(__name__)

# Default arguments for the DAG
default_args = {
    'owner': 'data_team',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# DAG definition
dag = DAG(
    'github_metrics_collection',
    default_args=default_args,
    description='Collect and analyze GitHub metrics for DORA and productivity tracking',
    schedule_interval='@daily',  # Run daily
    catchup=False,
    max_active_runs=1,
    tags=['github', 'metrics', 'dora', 'productivity']
)


def extract_github_data(**context):
    """
    Extract data from GitHub repositories.
    
    This task collects pull requests, deployments, issues, and commits
    from specified GitHub repositories.
    """
    # Get configuration from Airflow Variables
    github_token = Variable.get("GITHUB_TOKEN")
    repositories = Variable.get("GITHUB_REPOSITORIES", deserialize_json=True)
    collection_days = int(Variable.get("METRICS_COLLECTION_DAYS", "30"))
    
    collector = GitHubCollector(github_token)
    
    all_data = {
        'pull_requests': [],
        'deployments': [],
        'issues': [],
        'commits': [],
        'repositories': []
    }
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=collection_days)
    
    logger.info(f"Collecting data for {len(repositories)} repositories from {start_date} to {end_date}")
    
    for repo_name in repositories:
        try:
            logger.info(f"Processing repository: {repo_name}")
            
            # Collect repository info
            repo_info = collector.get_repository_info(repo_name)
            repo_info['repo_name'] = repo_name
            all_data['repositories'].append(repo_info)
            
            # Collect pull requests
            prs = collector.collect_pull_requests(
                repo_name=repo_name,
                since=start_date,
                until=end_date,
                state="all"
            )
            for pr in prs:
                pr['repo_name'] = repo_name
            all_data['pull_requests'].extend(prs)
            
            # Collect deployments
            deployments = collector.collect_deployments(
                repo_name=repo_name,
                since=start_date,
                until=end_date
            )
            for deployment in deployments:
                deployment['repo_name'] = repo_name
            all_data['deployments'].extend(deployments)
            
            # Collect issues
            issues = collector.collect_issues(
                repo_name=repo_name,
                since=start_date,
                until=end_date,
                state="all"
            )
            for issue in issues:
                issue['repo_name'] = repo_name
            all_data['issues'].extend(issues)
            
            # Collect commits
            commits = collector.collect_commits(
                repo_name=repo_name,
                since=start_date,
                until=end_date
            )
            for commit in commits:
                commit['repo_name'] = repo_name
            all_data['commits'].extend(commits)
            
            logger.info(f"Collected data from {repo_name}: "
                       f"{len(prs)} PRs, {len(deployments)} deployments, "
                       f"{len(issues)} issues, {len(commits)} commits")
                       
        except Exception as e:
            logger.error(f"Failed to collect data from {repo_name}: {e}")
            # Continue with other repositories
            continue
    
    # Store collected data for next tasks
    context['task_instance'].xcom_push(key='github_data', value=all_data)
    
    logger.info(f"Total data collected: "
               f"{len(all_data['pull_requests'])} PRs, "
               f"{len(all_data['deployments'])} deployments, "
               f"{len(all_data['issues'])} issues, "
               f"{len(all_data['commits'])} commits")
    
    return all_data


def calculate_dora_metrics(**context):
    """
    Calculate DORA metrics from collected GitHub data.
    """
    # Get data from previous task
    github_data = context['task_instance'].xcom_pull(
        task_ids='extract_github_data',
        key='github_data'
    )
    
    if not github_data:
        raise ValueError("No GitHub data found from extraction task")
    
    logger.info("Calculating DORA metrics...")
    
    # Initialize DORA metrics calculator
    dora_calculator = DORAMetrics(github_data)
    
    # Calculate all DORA metrics
    collection_days = int(Variable.get("METRICS_COLLECTION_DAYS", "30"))
    dora_metrics = dora_calculator.get_all_dora_metrics(period_days=collection_days)
    
    # Store metrics
    context['task_instance'].xcom_push(key='dora_metrics', value=dora_metrics)
    
    logger.info("DORA metrics calculated successfully")
    logger.info(f"Deployment frequency: {dora_metrics['deployment_frequency']['deployments_per_week']:.2f}/week")
    logger.info(f"Lead time: {dora_metrics['lead_time_for_changes']['median_lead_time_hours']:.2f} hours")
    logger.info(f"MTTR: {dora_metrics['mean_time_to_recovery']['mean_recovery_time_hours']:.2f} hours")
    logger.info(f"Change failure rate: {dora_metrics['change_failure_rate']['change_failure_rate']:.3f}")
    
    return dora_metrics


def calculate_pr_metrics(**context):
    """
    Calculate Pull Request specific metrics.
    """
    # Get data from extraction task
    github_data = context['task_instance'].xcom_pull(
        task_ids='extract_github_data',
        key='github_data'
    )
    
    if not github_data or not github_data['pull_requests']:
        logger.warning("No pull request data found")
        return {}
    
    logger.info("Calculating PR metrics...")
    
    # Initialize PR metrics calculator
    pr_calculator = PRMetrics(github_data['pull_requests'])
    
    # Calculate all PR metrics
    pr_metrics = {
        'cycle_time_analysis': pr_calculator.cycle_time_analysis(),
        'review_analysis': pr_calculator.review_analysis(),
        'merge_analysis': pr_calculator.merge_analysis()
    }
    
    # Store metrics
    context['task_instance'].xcom_push(key='pr_metrics', value=pr_metrics)
    
    logger.info("PR metrics calculated successfully")
    cycle_analysis = pr_metrics['cycle_time_analysis']
    if 'error' not in cycle_analysis:
        logger.info(f"Mean PR cycle time: {cycle_analysis['mean_cycle_time_hours']:.2f} hours")
        logger.info(f"Median PR cycle time: {cycle_analysis['median_cycle_time_hours']:.2f} hours")
    
    return pr_metrics


def calculate_productivity_metrics(**context):
    """
    Calculate developer productivity metrics.
    """
    # Get data from extraction task
    github_data = context['task_instance'].xcom_pull(
        task_ids='extract_github_data',
        key='github_data'
    )
    
    if not github_data:
        logger.warning("No GitHub data found")
        return {}
    
    logger.info("Calculating productivity metrics...")
    
    # Initialize productivity calculator
    productivity_calculator = ProductivityMetrics(github_data)
    
    # Calculate productivity metrics
    collection_days = int(Variable.get("METRICS_COLLECTION_DAYS", "30"))
    productivity_metrics = {
        'developer_activity': productivity_calculator.developer_activity(period_days=collection_days),
        'code_quality_trends': productivity_calculator.code_quality_trends(),
        'collaboration_metrics': productivity_calculator.collaboration_metrics()
    }
    
    # Store metrics
    context['task_instance'].xcom_push(key='productivity_metrics', value=productivity_metrics)
    
    logger.info("Productivity metrics calculated successfully")
    dev_activity = productivity_metrics['developer_activity']
    if 'commit_activity' in dev_activity:
        commit_stats = dev_activity['commit_activity']
        logger.info(f"Total commits: {commit_stats['total_commits']}")
        logger.info(f"Active contributors: {commit_stats['total_authors']}")
    
    return productivity_metrics


def store_metrics(**context):
    """
    Store all calculated metrics to database or file system.
    """
    # Get all metrics from previous tasks
    dora_metrics = context['task_instance'].xcom_pull(
        task_ids='calculate_dora_metrics',
        key='dora_metrics'
    )
    
    pr_metrics = context['task_instance'].xcom_pull(
        task_ids='calculate_pr_metrics',
        key='pr_metrics'
    )
    
    productivity_metrics = context['task_instance'].xcom_pull(
        task_ids='calculate_productivity_metrics',
        key='productivity_metrics'
    )
    
    # Combine all metrics
    all_metrics = {
        'timestamp': datetime.now().isoformat(),
        'dora_metrics': dora_metrics or {},
        'pr_metrics': pr_metrics or {},
        'productivity_metrics': productivity_metrics or {},
        'collection_period_days': int(Variable.get("METRICS_COLLECTION_DAYS", "30"))
    }
    
    # Store to file (in production, store to database)
    output_dir = Variable.get("METRICS_OUTPUT_DIR", "/tmp/github_metrics")
    os.makedirs(output_dir, exist_ok=True)
    
    # Create dated filename
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"github_metrics_{date_str}.json"
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, 'w') as f:
        json.dump(all_metrics, f, indent=2, default=str)
    
    logger.info(f"Metrics stored to {filepath}")
    
    # Also store latest metrics
    latest_filepath = os.path.join(output_dir, "latest_metrics.json")
    with open(latest_filepath, 'w') as f:
        json.dump(all_metrics, f, indent=2, default=str)
    
    context['task_instance'].xcom_push(key='all_metrics', value=all_metrics)
    
    return filepath


def generate_dashboard_data(**context):
    """
    Generate dashboard-ready data and charts.
    """
    # Get all metrics
    all_metrics = context['task_instance'].xcom_pull(
        task_ids='store_metrics',
        key='all_metrics'
    )
    
    if not all_metrics:
        logger.warning("No metrics data found for dashboard generation")
        return
    
    logger.info("Generating dashboard data...")
    
    # Create static charts
    try:
        charts = create_static_charts(all_metrics)
        
        # Store charts as JSON (for later use in dashboard)
        output_dir = Variable.get("METRICS_OUTPUT_DIR", "/tmp/github_metrics")
        charts_dir = os.path.join(output_dir, "charts")
        os.makedirs(charts_dir, exist_ok=True)
        
        date_str = datetime.now().strftime("%Y-%m-%d")
        
        for chart_name, fig in charts.items():
            chart_file = os.path.join(charts_dir, f"{chart_name}_{date_str}.json")
            fig.write_json(chart_file)
            logger.info(f"Chart saved: {chart_file}")
        
        logger.info("Dashboard data generated successfully")
        
    except Exception as e:
        logger.error(f"Failed to generate dashboard data: {e}")
        # Don't fail the entire DAG for dashboard generation issues
        pass


# Define tasks
extract_task = PythonOperator(
    task_id='extract_github_data',
    python_callable=extract_github_data,
    dag=dag,
    provide_context=True
)

dora_task = PythonOperator(
    task_id='calculate_dora_metrics',
    python_callable=calculate_dora_metrics,
    dag=dag,
    provide_context=True
)

pr_task = PythonOperator(
    task_id='calculate_pr_metrics',
    python_callable=calculate_pr_metrics,
    dag=dag,
    provide_context=True
)

productivity_task = PythonOperator(
    task_id='calculate_productivity_metrics',
    python_callable=calculate_productivity_metrics,
    dag=dag,
    provide_context=True
)

store_task = PythonOperator(
    task_id='store_metrics',
    python_callable=store_metrics,
    dag=dag,
    provide_context=True
)

dashboard_task = PythonOperator(
    task_id='generate_dashboard_data',
    python_callable=generate_dashboard_data,
    dag=dag,
    provide_context=True
)

# Define task dependencies
extract_task >> [dora_task, pr_task, productivity_task]
[dora_task, pr_task, productivity_task] >> store_task
store_task >> dashboard_task
