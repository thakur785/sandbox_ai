#!/usr/bin/env python3
"""
Philips GitHub Metrics Viewer
View team-specific metrics for Philips Internal organization
"""

import json
import sys
from datetime import datetime
from pathlib import Path
import subprocess

def test_philips_connection():
    """Test connection to Philips Internal organization."""
    print("🔍 Testing Philips Internal Access...")
    print("-" * 40)
    
    try:
        result = subprocess.run(['wsl', 'bash', '-c', 'source ~/airflow-venv/bin/activate && airflow variables get GITHUB_TOKEN'], 
                              capture_output=True, text=True)
        token = result.stdout.strip()
        
        if not token:
            print("❌ No GitHub token found")
            return False
        
        # Test the connection
        test_cmd = f'''
source ~/airflow-venv/bin/activate && python -c "
from github import Github
g = Github('{token}')
try:
    org = g.get_organization('philips-internal')
    print('✅ Connected to Philips Internal')
    print(f'   Organization: {{org.name or \"philips-internal\"}}')
    print(f'   Public repos: {{org.public_repos}}')
    print(f'   Private repos: {{org.total_private_repos}}')
    
    # Try to access team
    try:
        team = org.get_team_by_slug('hpm-synergy-blr')
        print(f'✅ Team access: {{team.name}} ({{team.members_count}} members)')
    except Exception as e:
        print(f'⚠️  Team access limited: {{str(e)[:50]}}...')
        
except Exception as e:
    print(f'❌ Access denied: {{str(e)[:100]}}...')
"
'''
        
        result = subprocess.run(['wsl', 'bash', '-c', test_cmd], 
                              capture_output=True, text=True)
        
        if result.stdout:
            print(result.stdout)
            return "✅ Connected" in result.stdout
        else:
            print("❌ Connection test failed")
            if result.stderr:
                print(f"Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def view_philips_metrics():
    """View Philips metrics if available."""
    print("\n📊 Philips Metrics Dashboard")
    print("=" * 50)
    
    # Check for Philips metrics files
    possible_paths = [
        "/tmp/philips_metrics_output/latest_philips_metrics.json",
        "./philips_metrics.json",
        "/tmp/github_metrics_output/latest_metrics.json"
    ]
    
    metrics_file = None
    for path in possible_paths:
        # Convert WSL path for access
        if path.startswith("/tmp/"):
            wsl_path = f"wsl_path_{path.replace('/', '_')}.json"
            try:
                subprocess.run(['wsl', 'bash', '-c', f'cp {path} /tmp/{wsl_path}'], 
                             capture_output=True)
                if Path(f"/tmp/{wsl_path}").exists():
                    metrics_file = f"/tmp/{wsl_path}"
                    break
            except:
                continue
        elif Path(path).exists():
            metrics_file = path
            break
    
    if not metrics_file:
        print("❌ No Philips metrics found yet.")
        print("\n💡 To collect Philips metrics:")
        print("   1. Ensure you have access to philips-internal organization")
        print("   2. Run: airflow dags trigger philips_github_metrics")
        print("   3. Wait for collection to complete (~10-15 minutes)")
        return
    
    try:
        with open(metrics_file, 'r') as f:
            metrics = json.load(f)
        
        print("🎉 Philips Metrics Found!")
        
        # Show organization summary if available
        if 'organization' in metrics:
            org = metrics['organization']
            print(f"\n🏢 Organization: {org.get('name', 'philips-internal')}")
            print(f"   📊 Public repos: {org.get('public_repos', 0)}")
            print(f"   🔒 Private repos: {org.get('private_repos', 0)}")
            print(f"   👥 Members: {org.get('members_count', 0)}")
        
        # Show team information if available
        if 'team' in metrics:
            team = metrics['team']
            print(f"\n👥 Team: {team.get('name', 'hpm-synergy-blr')}")
            print(f"   📋 Members: {team.get('members_count', 0)}")
            print(f"   🔒 Privacy: {team.get('privacy', 'unknown')}")
        
        # Show repository metrics
        if 'metrics' in metrics and metrics['metrics']:
            print(f"\n📦 Repository Analysis:")
            print("-" * 30)
            
            total_repos = 0
            total_prs = 0
            total_team_prs = 0
            total_issues = 0
            
            for repo_name, repo_data in metrics['metrics'].items():
                if 'error' in repo_data:
                    print(f"\n❌ {repo_name}: {repo_data['error']}")
                    continue
                
                total_repos += 1
                prs = repo_data.get('pull_requests', [])
                issues = repo_data.get('issues', [])
                team_analysis = repo_data.get('team_analysis', {})
                
                team_prs = team_analysis.get('team_prs', [])
                team_issues = team_analysis.get('team_issues', [])
                
                total_prs += len(prs)
                total_team_prs += len(team_prs)
                total_issues += len(issues)
                
                print(f"\n📦 {repo_name}:")
                print(f"   🔄 Total PRs: {len(prs)}")
                print(f"   👥 Team PRs: {len(team_prs)} ({len(team_prs)/len(prs)*100:.1f}% of total)" if prs else "   👥 Team PRs: 0")
                print(f"   🐛 Total Issues: {len(issues)}")
                print(f"   👥 Team Issues: {len(team_issues)} ({len(team_issues)/len(issues)*100:.1f}% of total)" if issues else "   👥 Team Issues: 0")
                
                # Show recent team activity
                if team_prs:
                    recent_pr = max(team_prs, key=lambda x: x['created_at'])
                    print(f"   📅 Latest team PR: #{recent_pr['number']} by {recent_pr['author']}")
                
                # Show language and repo info
                repo_info = repo_data.get('repository', {})
                if repo_info.get('language'):
                    print(f"   💻 Language: {repo_info['language']}")
                
                # PR size analysis for team
                if team_prs:
                    avg_additions = sum(pr.get('additions', 0) for pr in team_prs) / len(team_prs)
                    avg_changes = sum(pr.get('changed_files', 0) for pr in team_prs) / len(team_prs)
                    print(f"   📏 Avg team PR size: {avg_additions:.0f} lines, {avg_changes:.0f} files")
            
            # Overall summary
            print(f"\n📈 Overall Team Impact:")
            print(f"   📊 Repositories analyzed: {total_repos}")
            print(f"   🔄 Total PRs: {total_prs}")
            print(f"   👥 Team PRs: {total_team_prs} ({total_team_prs/total_prs*100:.1f}% of all PRs)" if total_prs else "   👥 Team PRs: 0")
            print(f"   🐛 Total Issues: {total_issues}")
            
            # Show team members analyzed
            team_members = repo_data.get('team_members_analyzed', [])
            if team_members:
                print(f"   👥 Team members tracked: {len(team_members)}")
                print(f"      {', '.join(team_members[:5])}{'...' if len(team_members) > 5 else ''}")
        
        elif 'repositories' in metrics:
            # Show repository discovery results
            repos = metrics['repositories']
            print(f"\n📦 Discovered {len(repos)} Philips repositories:")
            for i, repo in enumerate(repos[:10], 1):
                print(f"   {i:2d}. {repo['name']} ({repo.get('language', 'Unknown')})")
                print(f"       ⭐ {repo.get('stars', 0)} stars | 🐛 {repo.get('open_issues', 0)} issues")
            
            if len(repos) > 10:
                print(f"       ... and {len(repos) - 10} more repositories")
        
        print(f"\n📁 Full metrics: {metrics_file}")
        
    except Exception as e:
        print(f"❌ Error reading metrics: {e}")

def trigger_philips_collection():
    """Trigger Philips metrics collection."""
    print("\n🚀 Triggering Philips Metrics Collection")
    print("-" * 40)
    
    try:
        # Unpause the DAG
        result = subprocess.run(['wsl', 'bash', '-c', 'source ~/airflow-venv/bin/activate && airflow dags unpause philips_github_metrics'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ DAG unpaused")
        else:
            print(f"⚠️  DAG unpause result: {result.stderr}")
        
        # Trigger the DAG
        result = subprocess.run(['wsl', 'bash', '-c', 'source ~/airflow-venv/bin/activate && airflow dags trigger philips_github_metrics'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Philips metrics collection triggered!")
            print("   🌐 Monitor progress: http://localhost:8080/dags/philips_github_metrics")
            print("   ⏱️  Expected completion: 10-15 minutes")
            print("   📁 Results will be saved to: /tmp/philips_metrics_output/")
        else:
            print(f"❌ Failed to trigger DAG: {result.stderr}")
        
    except Exception as e:
        print(f"❌ Trigger failed: {e}")

def show_philips_usage():
    """Show usage instructions for Philips metrics."""
    print("\n💡 Philips GitHub Metrics Usage Guide")
    print("=" * 50)
    
    print("\n🔧 Prerequisites:")
    print("   ✅ GitHub token with philips-internal org access")
    print("   ✅ Token scopes: repo, read:org, read:user")
    print("   ✅ Member of philips-internal organization")
    print("   ✅ Access to hpm-synergy-blr team (optional)")
    
    print("\n📋 Commands:")
    print("   python view_philips_metrics.py              # View current metrics")
    print("   python view_philips_metrics.py --test       # Test org access")
    print("   python view_philips_metrics.py --trigger    # Start collection")
    print("   python view_philips_metrics.py --help       # Show this help")
    
    print("\n🌐 Airflow Dashboard:")
    print("   http://localhost:8080/dags/philips_github_metrics")
    
    print("\n📊 What You'll Get:")
    print("   🔄 Team vs external PR analysis")
    print("   👥 Individual team member contributions")
    print("   📈 DORA metrics for team repositories")
    print("   🐛 Issue resolution patterns")
    print("   📏 Code review and PR size analysis")
    
    print("\n🎯 Team Analysis Features:")
    print("   • Filters data by hpm-synergy-blr team members")
    print("   • Compares team vs external contributions")
    print("   • Tracks collaboration patterns")
    print("   • Measures team productivity trends")

if __name__ == "__main__":
    print("🎯 Philips GitHub Metrics Viewer")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--test":
            test_philips_connection()
        elif sys.argv[1] == "--trigger":
            trigger_philips_collection()
        elif sys.argv[1] == "--help":
            show_philips_usage()
        else:
            print("❌ Unknown option. Use --help for usage guide.")
    else:
        # Default: test connection and show metrics
        connection_ok = test_philips_connection()
        
        if connection_ok:
            view_philips_metrics()
        else:
            print("\n💡 Connection Issues - Troubleshooting:")
            print("   1. Verify your GitHub token has org access")
            print("   2. Ensure you're a member of philips-internal")
            print("   3. Check token scopes include 'read:org'")
            print("   4. Try: python view_philips_metrics.py --help")
