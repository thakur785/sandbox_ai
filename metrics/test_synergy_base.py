#!/usr/bin/env python3
"""
Test access to synergy-base repository and hpm-synergy-blr team
"""

import subprocess
import sys

def test_synergy_base_access():
    """Test access to specific repository and team."""
    
    print("🎯 Testing synergy-base Repository and Team Access...")
    
    # Get GitHub token
    try:
        result = subprocess.run(['wsl', 'bash', '-c', 'source ~/airflow-venv/bin/activate && airflow variables get GITHUB_TOKEN'], 
                              capture_output=True, text=True, timeout=30)
        token = result.stdout.strip()
        
        if not token:
            print("❌ No GitHub token found")
            return False
            
        print(f"✅ GitHub token found")
        
    except Exception as e:
        print(f"❌ Token retrieval failed: {e}")
        return False
    
    # Test specific repository and team access
    test_script = f"""
from github import Github
import sys

try:
    g = Github('{token}')
    
    # Test rate limit
    rate_limit = g.get_rate_limit()
    print(f'📊 Rate limit: {{rate_limit.core.remaining}}/{{rate_limit.core.limit}}')
    
    # Test specific repository access
    try:
        repo = g.get_repo('philips-internal/synergy-base')
        print(f'✅ Repository access: {{repo.full_name}}')
        print(f'   📝 Description: {{repo.description or "No description"}}')
        print(f'   🔤 Language: {{repo.language or "Unknown"}}')
        print(f'   ⭐ Stars: {{repo.stargazers_count}}')
        print(f'   🔀 Forks: {{repo.forks_count}}')
        print(f'   📅 Updated: {{repo.updated_at.strftime("%Y-%m-%d")}}')
        
        # Get recent pull requests
        prs = list(repo.get_pulls(state='all', sort='updated')[:3])
        print(f'   📋 Recent PRs ({{len(prs)}}):')
        for pr in prs:
            print(f'      - #{{pr.number}} {{pr.title[:50]}}... ({{pr.state}})')
            
    except Exception as repo_error:
        print(f'❌ Repository access denied: {{str(repo_error)[:150]}}')
        sys.exit(1)
    
    # Test team access
    try:
        org = g.get_organization('philips-internal')
        team = org.get_team_by_slug('hpm-synergy-blr')
        print(f'\\n✅ Team access: {{team.name}}')
        print(f'   👥 Members: {{team.members_count}}')
        
        # List team members
        members = list(team.get_members())
        print(f'   📋 Team members ({{len(members)}}):')
        for member in members[:10]:  # Show first 10
            print(f'      - {{member.login}} ({{member.name or "No name"}})')
            
        # Check if team has access to the repository
        try:
            team_repos = list(team.get_repos())
            synergy_in_team = any(r.name == 'synergy-base' for r in team_repos)
            if synergy_in_team:
                print(f'   ✅ Team has access to synergy-base repository')
            else:
                print(f'   ⚠️  Team may not have direct access to synergy-base')
                print(f'   📦 Team repositories ({{len(team_repos)}}):')
                for repo in team_repos[:5]:
                    print(f'      - {{repo.full_name}}')
        except Exception as team_repo_error:
            print(f'   ⚠️  Cannot check team repository access: {{str(team_repo_error)[:100]}}')
            
    except Exception as team_error:
        print(f'❌ Team access denied: {{str(team_error)[:150]}}')
        print('   This might be normal if team is private')
    
    print('\\n🎉 Access test completed successfully!')
    sys.exit(0)
        
except Exception as e:
    print(f'❌ GitHub connection failed: {{str(e)[:150]}}')
    sys.exit(1)
"""
    
    try:
        result = subprocess.run(['wsl', 'bash', '-c', f'source ~/airflow-venv/bin/activate && python3 -c "{test_script}"'], 
                              capture_output=True, text=True, timeout=60)
        
        print(result.stdout)
        
        if result.stderr:
            print(f"⚠️  Warnings: {result.stderr}")
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("⏰ Test timed out")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    print("🎯 Synergy-Base Repository & Team Access Test")
    print("=" * 60)
    
    success = test_synergy_base_access()
    
    if success:
        print("\n✅ Ready to analyze synergy-base metrics!")
        print("\n🚀 Next steps:")
        print("   1. Monitor DAG execution: http://localhost:8080/dags/philips_github_metrics")
        print("   2. View collected data: python view_philips_metrics.py")
        print("   3. Check for output files in current directory")
    else:
        print("\n❌ Access issues detected")
        print("\n🔧 Please check:")
        print("   1. Your GitHub token has access to philips-internal organization")
        print("   2. You have access to the synergy-base repository")
        print("   3. Team permissions are configured correctly")
