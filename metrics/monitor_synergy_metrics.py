#!/usr/bin/env python3
"""
Monitor Philips Synergy-Base Metrics Collection
"""

import subprocess
import sys
import time
import json
import os
from datetime import datetime

def check_dag_status():
    """Check the status of the Philips DAG."""
    
    try:
        result = subprocess.run(['wsl', 'bash', '-c', 'source ~/airflow-venv/bin/activate && airflow dags list-runs philips_github_metrics --limit 1'], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if 'manual__' in line:
                    parts = line.split('|')
                    if len(parts) >= 3:
                        state = parts[2].strip()
                        run_id = parts[1].strip()
                        return state, run_id
        
        return "unknown", "unknown"
        
    except Exception as e:
        print(f"⚠️  Could not check DAG status: {e}")
        return "error", "error"

def check_output_files():
    """Check for generated output files."""
    
    files_to_check = [
        'philips_github_metrics.json',
        'philips_github_metrics.html',
        'philips_dora_metrics.json',
        'philips_team_analysis.json'
    ]
    
    found_files = []
    for file in files_to_check:
        if os.path.exists(file):
            size = os.path.getsize(file)
            modified = datetime.fromtimestamp(os.path.getmtime(file))
            found_files.append({
                'file': file,
                'size': size,
                'modified': modified.strftime('%Y-%m-%d %H:%M:%S')
            })
    
    return found_files

def display_metrics_summary(file_path):
    """Display a summary of collected metrics."""
    
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        print(f"\n📊 Metrics Summary from {file_path}:")
        print("=" * 50)
        
        if 'repositories' in data:
            for repo_name, repo_data in data['repositories'].items():
                print(f"\n🏪 Repository: {repo_name}")
                
                if 'info' in repo_data:
                    info = repo_data['info']
                    print(f"   📝 Description: {info.get('description', 'No description')}")
                    print(f"   🔤 Language: {info.get('language', 'Unknown')}")
                    print(f"   ⭐ Stars: {info.get('stargazers_count', 0)}")
                    print(f"   🔀 Forks: {info.get('forks_count', 0)}")
                
                if 'pull_requests' in repo_data:
                    prs = repo_data['pull_requests']
                    total_prs = len(prs)
                    open_prs = len([pr for pr in prs if pr.get('state') == 'open'])
                    closed_prs = len([pr for pr in prs if pr.get('state') == 'closed'])
                    merged_prs = len([pr for pr in prs if pr.get('merged')])
                    
                    print(f"\n   📋 Pull Requests:")
                    print(f"      Total: {total_prs}")
                    print(f"      Open: {open_prs}")
                    print(f"      Closed: {closed_prs}")
                    print(f"      Merged: {merged_prs}")
                
                if 'team_activity' in repo_data:
                    team_activity = repo_data['team_activity']
                    print(f"\n   👥 Team Activity:")
                    print(f"      Team members with activity: {len(team_activity)}")
                    for member, activity in list(team_activity.items())[:5]:
                        print(f"      - {member}: {len(activity.get('pull_requests', []))} PRs")
        
        # Check for DORA metrics
        if 'dora_metrics' in data:
            dora = data['dora_metrics']
            print(f"\n🎯 DORA Metrics:")
            print(f"   Deployment Frequency: {dora.get('deployment_frequency', 'N/A')}")
            print(f"   Lead Time: {dora.get('lead_time_for_changes', 'N/A')}")
            print(f"   Change Failure Rate: {dora.get('change_failure_rate', 'N/A')}")
            print(f"   Recovery Time: {dora.get('time_to_restore_service', 'N/A')}")
        
    except Exception as e:
        print(f"⚠️  Could not read metrics file: {e}")

def monitor_philips_metrics():
    """Monitor the Philips metrics collection process."""
    
    print("🎯 Monitoring Philips Synergy-Base Metrics Collection")
    print("=" * 60)
    
    # Check current DAG status
    print("\n🔍 Checking DAG Status...")
    state, run_id = check_dag_status()
    print(f"   Current state: {state}")
    print(f"   Run ID: {run_id}")
    
    # Check for existing output files
    print("\n📁 Checking Output Files...")
    output_files = check_output_files()
    
    if output_files:
        print("   Found files:")
        for file_info in output_files:
            print(f"      - {file_info['file']} ({file_info['size']} bytes, modified: {file_info['modified']})")
        
        # Display summary of the most recent metrics file
        for file_info in output_files:
            if file_info['file'].endswith('.json') and 'github_metrics' in file_info['file']:
                display_metrics_summary(file_info['file'])
                break
    else:
        print("   No output files found yet")
    
    # Monitor progress if DAG is running
    if state in ['queued', 'running']:
        print(f"\n⏳ DAG is {state}... monitoring progress")
        print("   You can also check: http://localhost:8080/dags/philips_github_metrics")
        
        # Wait and check again
        for i in range(12):  # Check for 2 minutes
            time.sleep(10)
            new_state, _ = check_dag_status()
            
            if new_state != state:
                print(f"\n🔄 Status changed: {state} → {new_state}")
                state = new_state
                
                if state in ['success', 'failed']:
                    break
        
        # Final check for output files
        if state == 'success':
            print("\n✅ DAG completed successfully!")
            final_files = check_output_files()
            if final_files:
                print("\n📊 Final Results:")
                for file_info in final_files:
                    print(f"   - {file_info['file']} ({file_info['size']} bytes)")
                
                # Display the main metrics summary
                for file_info in final_files:
                    if file_info['file'] == 'philips_github_metrics.json':
                        display_metrics_summary(file_info['file'])
                        break
        elif state == 'failed':
            print("\n❌ DAG failed! Check the Airflow UI for details:")
            print("   http://localhost:8080/dags/philips_github_metrics")
    
    elif state == 'success':
        print("\n✅ DAG has already completed successfully!")
        
    elif state == 'failed':
        print("\n❌ DAG failed! Check the Airflow UI for details:")
        print("   http://localhost:8080/dags/philips_github_metrics")
    
    print(f"\n🚀 Next Steps:")
    print("   1. View detailed results: python view_philips_metrics.py")
    print("   2. Open dashboard: http://localhost:8080/dags/philips_github_metrics")
    print("   3. Check output files for detailed data")
    
    return state == 'success'

if __name__ == "__main__":
    success = monitor_philips_metrics()
    sys.exit(0 if success else 1)
