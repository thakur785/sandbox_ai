"""
Philips Internal GitHub Metrics DAG
Specialized for philips-internal organization and hpm-synergy-blr team
"""

from datetime import datetime, timedelta
import json
import os
import logging
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable

logger = logging.getLogger(__name__)

# Default arguments for the DAG
default_args = {
    'owner': 'philips_team',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# DAG definition
dag = DAG(
    'philips_github_metrics',
    default_args=default_args,
    description='Philips Internal GitHub metrics collection with team analysis',
    schedule='@daily',
    catchup=False,
    max_active_runs=1,
    tags=['philips', 'github', 'metrics', 'dora', 'team-analysis']
)

def collect_philips_repositories(**context):
    """Discover and collect Philips Internal repositories."""
    try:
        github_token = Variable.get("GITHUB_TOKEN", default_var=None)
        
        if not github_token:
            logger.error("GitHub token not configured")
            return {"status": "error", "message": "GitHub token required"}
        
        from github import Github
        
        g = Github(github_token)
        
        # Get Philips Internal organization
        try:
            org = g.get_organization('philips-internal')
            logger.info(f"Connected to organization: {org.name or 'philips-internal'}")
            
            # Get organization repositories (limit to most active ones)
            repos = []
            repo_count = 0
            
            for repo in org.get_repos(sort='updated', direction='desc'):
                if repo_count >= 20:  # Limit to top 20 most active repos
                    break
                
                # Skip archived repositories
                if repo.archived:
                    continue
                
                repo_info = {
                    'name': repo.full_name,
                    'description': repo.description,
                    'language': repo.language,
                    'stars': repo.stargazers_count,
                    'forks': repo.forks_count,
                    'open_issues': repo.open_issues_count,
                    'size': repo.size,
                    'updated_at': repo.updated_at.isoformat(),
                    'default_branch': repo.default_branch,
                    'archived': repo.archived,
                    'private': repo.private
                }
                
                repos.append(repo_info)
                repo_count += 1
                logger.info(f"Added repository: {repo.full_name}")
            
            logger.info(f"Collected {len(repos)} Philips repositories")
            
            return {
                "status": "success",
                "organization": {
                    "name": org.name or "philips-internal",
                    "public_repos": org.public_repos,
                    "private_repos": org.total_private_repos,
                    "members_count": org.get_members().totalCount
                },
                "repositories": repos
            }
            
        except Exception as org_error:
            logger.error(f"Cannot access philips-internal organization: {org_error}")
            return {
                "status": "error", 
                "message": f"Organization access denied: {org_error}",
                "suggestions": [
                    "Verify your GitHub token has 'read:org' permissions",
                    "Ensure you're a member of philips-internal organization",
                    "Check if organization name is correct"
                ]
            }
        
    except Exception as e:
        logger.error(f"Repository collection failed: {str(e)}")
        return {"status": "error", "message": str(e)}

def collect_team_members(**context):
    """Collect hpm-synergy-blr team members."""
    try:
        github_token = Variable.get("GITHUB_TOKEN", default_var=None)
        
        if not github_token:
            return {"status": "error", "message": "GitHub token required"}
        
        from github import Github
        
        g = Github(github_token)
        org = g.get_organization('philips-internal')
        
        team_members = []
        team_info = {}
        
        try:
            # Try to get the specific team
            team = org.get_team_by_slug('hpm-synergy-blr')
            
            team_info = {
                "name": team.name,
                "slug": team.slug,
                "description": team.description,
                "members_count": team.members_count,
                "privacy": team.privacy
            }
            
            # Get team members
            for member in team.get_members():
                member_info = {
                    'login': member.login,
                    'name': member.name,
                    'email': member.email,
                    'company': member.company,
                    'location': member.location,
                    'public_repos': member.public_repos,
                    'followers': member.followers,
                    'following': member.following,
                    'created_at': member.created_at.isoformat() if member.created_at else None,
                    'updated_at': member.updated_at.isoformat() if member.updated_at else None
                }
                team_members.append(member_info)
            
            logger.info(f"Collected {len(team_members)} team members from {team.name}")
            
            return {
                "status": "success",
                "team": team_info,
                "members": team_members
            }
            
        except Exception as team_error:
            logger.warning(f"Cannot access team 'hpm-synergy-blr': {team_error}")
            
            # Try to list available teams
            accessible_teams = []
            try:
                for team in org.get_teams():
                    accessible_teams.append({
                        'name': team.name,
                        'slug': team.slug,
                        'members_count': team.members_count
                    })
            except:
                pass
            
            return {
                "status": "partial",
                "message": f"Cannot access hpm-synergy-blr team: {team_error}",
                "accessible_teams": accessible_teams,
                "suggestions": [
                    "Team might be private",
                    "Check if team slug is correct",
                    "Verify your permissions to read team information"
                ]
            }
        
    except Exception as e:
        logger.error(f"Team collection failed: {str(e)}")
        return {"status": "error", "message": str(e)}

def collect_detailed_philips_metrics(**context):
    """Collect detailed metrics from Philips repositories with team member filtering."""
    try:
        # Get data from previous tasks
        repo_data = context['task_instance'].xcom_pull(task_ids='collect_philips_repositories')
        team_data = context['task_instance'].xcom_pull(task_ids='collect_team_members')
        
        if not repo_data or repo_data.get('status') != 'success':
            logger.error("No repository data available")
            return {"status": "error", "message": "No repository data"}
        
        github_token = Variable.get("GITHUB_TOKEN", default_var=None)
        from github import Github
        from datetime import datetime, timedelta
        
        g = Github(github_token)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)  # Last 30 days
        
        # Get team member usernames for filtering
        team_members = []
        if team_data and team_data.get('status') == 'success':
            team_members = [member['login'] for member in team_data.get('members', [])]
            logger.info(f"Filtering for team members: {team_members}")
        
        all_metrics = {}
        repositories = repo_data.get('repositories', [])[:5]  # Limit to top 5 repos
        
        for repo_info in repositories:
            repo_name = repo_info['name']
            
            try:
                logger.info(f"Collecting metrics for {repo_name}...")
                repo = g.get_repo(repo_name)
                
                # Collect PRs with team member filtering
                prs = []
                for pr in repo.get_pulls(state='all', sort='updated', direction='desc'):
                    if pr.created_at >= start_date:
                        # Check if PR is from team member
                        is_team_member = not team_members or pr.user.login in team_members
                        
                        pr_data = {
                            'number': pr.number,
                            'title': pr.title,
                            'state': pr.state,
                            'created_at': pr.created_at.isoformat(),
                            'updated_at': pr.updated_at.isoformat(),
                            'merged_at': pr.merged_at.isoformat() if pr.merged_at else None,
                            'closed_at': pr.closed_at.isoformat() if pr.closed_at else None,
                            'author': pr.user.login,
                            'author_name': pr.user.name,
                            'is_team_member': is_team_member,
                            'additions': pr.additions,
                            'deletions': pr.deletions,
                            'changed_files': pr.changed_files,
                            'comments': pr.comments,
                            'review_comments': pr.review_comments,
                            'commits': pr.commits
                        }
                        
                        # Add reviewer information
                        reviewers = []
                        try:
                            for review in pr.get_reviews():
                                reviewer_info = {
                                    'user': review.user.login,
                                    'state': review.state,
                                    'submitted_at': review.submitted_at.isoformat() if review.submitted_at else None,
                                    'is_team_member': not team_members or review.user.login in team_members
                                }
                                reviewers.append(reviewer_info)
                            pr_data['reviewers'] = reviewers
                        except:
                            pr_data['reviewers'] = []
                        
                        prs.append(pr_data)
                    
                    if len(prs) >= 50:  # Limit to avoid rate limits
                        break
                
                # Collect issues with team member filtering
                issues = []
                for issue in repo.get_issues(state='all', sort='updated', direction='desc'):
                    if issue.created_at >= start_date and not issue.pull_request:
                        is_team_member = not team_members or issue.user.login in team_members
                        
                        issue_data = {
                            'number': issue.number,
                            'title': issue.title,
                            'state': issue.state,
                            'created_at': issue.created_at.isoformat(),
                            'updated_at': issue.updated_at.isoformat(),
                            'closed_at': issue.closed_at.isoformat() if issue.closed_at else None,
                            'author': issue.user.login,
                            'author_name': issue.user.name,
                            'is_team_member': is_team_member,
                            'comments': issue.comments,
                            'labels': [label.name for label in issue.labels]
                        }
                        issues.append(issue_data)
                    
                    if len(issues) >= 30:
                        break
                
                repo_metrics = {
                    'repository': repo_info,
                    'pull_requests': prs,
                    'issues': issues,
                    'team_analysis': {
                        'team_prs': [pr for pr in prs if pr['is_team_member']],
                        'team_issues': [issue for issue in issues if issue['is_team_member']],
                        'external_prs': [pr for pr in prs if not pr['is_team_member']],
                        'external_issues': [issue for issue in issues if not issue['is_team_member']]
                    },
                    'collection_date': datetime.now().isoformat(),
                    'period_start': start_date.isoformat(),
                    'period_end': end_date.isoformat(),
                    'team_members_analyzed': team_members
                }
                
                all_metrics[repo_name] = repo_metrics
                logger.info(f"Collected {len(prs)} PRs and {len(issues)} issues for {repo_name}")
                
                # Log team-specific stats
                team_prs = len([pr for pr in prs if pr['is_team_member']])
                team_issues = len([issue for issue in issues if issue['is_team_member']])
                logger.info(f"Team-specific: {team_prs} PRs, {team_issues} issues")
                
            except Exception as e:
                logger.error(f"Failed to collect metrics for {repo_name}: {str(e)}")
                all_metrics[repo_name] = {"error": str(e)}
        
        logger.info(f"Successfully collected metrics for {len(all_metrics)} repositories")
        return {"status": "success", "metrics": all_metrics}
        
    except Exception as e:
        logger.error(f"Metrics collection failed: {str(e)}")
        return {"status": "error", "message": str(e)}

def save_philips_metrics(**context):
    """Save Philips metrics to files with team analysis."""
    try:
        # Get data from previous tasks
        metrics_data = context['task_instance'].xcom_pull(task_ids='collect_detailed_philips_metrics')
        
        if not metrics_data or metrics_data.get('status') != 'success':
            logger.error("No metrics data to save")
            return {"status": "error", "message": "No metrics data"}
        
        # Create output directory
        output_dir = "/tmp/philips_metrics_output"
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save detailed metrics
        metrics_file = f"{output_dir}/philips_metrics_{timestamp}.json"
        with open(metrics_file, 'w') as f:
            json.dump(metrics_data, f, indent=2)
        
        # Create team summary
        team_summary = {
            "timestamp": timestamp,
            "total_repositories": len(metrics_data.get('metrics', {})),
            "repositories": {}
        }
        
        for repo_name, repo_data in metrics_data.get('metrics', {}).items():
            if 'error' in repo_data:
                continue
            
            team_analysis = repo_data.get('team_analysis', {})
            team_summary['repositories'][repo_name] = {
                "total_prs": len(repo_data.get('pull_requests', [])),
                "team_prs": len(team_analysis.get('team_prs', [])),
                "external_prs": len(team_analysis.get('external_prs', [])),
                "total_issues": len(repo_data.get('issues', [])),
                "team_issues": len(team_analysis.get('team_issues', [])),
                "external_issues": len(team_analysis.get('external_issues', []))
            }
        
        # Save team summary
        summary_file = f"{output_dir}/philips_team_summary_{timestamp}.json"
        with open(summary_file, 'w') as f:
            json.dump(team_summary, f, indent=2)
        
        # Save as latest
        latest_file = f"{output_dir}/latest_philips_metrics.json"
        with open(latest_file, 'w') as f:
            json.dump(metrics_data, f, indent=2)
        
        logger.info(f"Philips metrics saved:")
        logger.info(f"  Detailed: {metrics_file}")
        logger.info(f"  Summary: {summary_file}")
        logger.info(f"  Latest: {latest_file}")
        
        return {
            "status": "success",
            "files_created": [metrics_file, summary_file, latest_file],
            "output_directory": output_dir
        }
        
    except Exception as e:
        logger.error(f"Save failed: {str(e)}")
        return {"status": "error", "message": str(e)}

# Define tasks
collect_repos_task = PythonOperator(
    task_id='collect_philips_repositories',
    python_callable=collect_philips_repositories,
    dag=dag
)

collect_team_task = PythonOperator(
    task_id='collect_team_members',
    python_callable=collect_team_members,
    dag=dag
)

collect_metrics_task = PythonOperator(
    task_id='collect_detailed_philips_metrics',
    python_callable=collect_detailed_philips_metrics,
    dag=dag
)

save_metrics_task = PythonOperator(
    task_id='save_philips_metrics',
    python_callable=save_philips_metrics,
    dag=dag
)

# Set task dependencies
[collect_repos_task, collect_team_task] >> collect_metrics_task >> save_metrics_task
