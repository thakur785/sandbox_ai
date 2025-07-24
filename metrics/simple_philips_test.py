#!/usr/bin/env python3
"""
Direct Philips Access Test
"""

import subprocess
import sys

def simple_philips_test():
    """Simple test for Philips access."""
    
    print("🔍 Testing Philips Internal Access...")
    
    # Get GitHub token
    try:
        result = subprocess.run(['wsl', 'bash', '-c', 'source ~/airflow-venv/bin/activate && airflow variables get GITHUB_TOKEN'], 
                              capture_output=True, text=True, timeout=30)
        token = result.stdout.strip()
        
        if not token:
            print("❌ No GitHub token found in Airflow variables")
            print("💡 Set your token with:")
            print("   wsl bash -c \"source ~/airflow-venv/bin/activate && airflow variables set GITHUB_TOKEN 'your_token_here'\"")
            return False
            
        print(f"✅ GitHub token found (length: {len(token)})")
        
    except subprocess.TimeoutExpired:
        print("⏰ Token retrieval timed out")
        return False
    except Exception as e:
        print(f"❌ Token retrieval failed: {e}")
        return False
    
    # Test organization access
    test_script = f"""
from github import Github
import sys

try:
    g = Github('{token}')
    
    # Test rate limit
    rate_limit = g.get_rate_limit()
    print(f'📊 Rate limit: {{rate_limit.core.remaining}}/{{rate_limit.core.limit}}')
    
    # Test user
    user = g.get_user()
    print(f'👤 Authenticated as: {{user.login}}')
    
    # Test organization access
    try:
        org = g.get_organization('philips-internal')
        print(f'✅ Organization access: {{org.name or "philips-internal"}}')
        print(f'   📦 Public repos: {{org.public_repos}}')
        print(f'   🔒 Private repos: {{org.total_private_repos}}')
        print(f'   👥 Members: {{org.get_members().totalCount}}')
        
        # List some repositories
        repos = list(org.get_repos(sort='updated')[:5])
        print(f'   📋 Recent repositories:')
        for repo in repos:
            print(f'      - {{repo.full_name}} ({{repo.language or "Unknown"}})')
        
        # Test team access
        try:
            team = org.get_team_by_slug('hpm-synergy-blr')
            print(f'✅ Team access: {{team.name}} ({{team.members_count}} members)')
            
            # List some team members
            members = list(team.get_members()[:5])
            print(f'   👥 Team members (sample):')
            for member in members:
                print(f'      - {{member.login}} ({{member.name or "No name"}})')
                
        except Exception as team_error:
            print(f'⚠️  Team access limited: {{str(team_error)[:100]}}')
            print('   This might be normal if team is private')
        
        print('\\n🎉 Philips Internal access confirmed!')
        sys.exit(0)
        
    except Exception as org_error:
        print(f'❌ Organization access denied: {{str(org_error)[:150]}}')
        print('   Possible reasons:')
        print('   - Token lacks read:org permissions')
        print('   - Not a member of philips-internal organization')
        print('   - Organization name might be different')
        sys.exit(1)
        
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
        print("⏰ Organization test timed out")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def configure_philips_variables():
    """Configure Airflow variables for Philips."""
    
    print("\n🔧 Configuring Philips Variables...")
    
    # Suggest repositories based on common patterns
    suggested_repos = [
        "philips-internal/healthcare-platform",
        "philips-internal/medical-imaging",
        "philips-internal/patient-monitoring",
        "philips-internal/diagnostics-ai",
        "philips-internal/cloud-services"
    ]
    
    print("💡 Suggested repository patterns to look for:")
    for repo in suggested_repos:
        print(f"   - {repo}")
    
    print("\n🚀 To configure for specific repositories:")
    print("   1. First, run this test to see available repositories")
    print("   2. Then set specific repos:")
    print("      wsl bash -c \"source ~/airflow-venv/bin/activate && airflow variables set PHILIPS_REPOSITORIES '[\\\"philips-internal/repo1\\\", \\\"philips-internal/repo2\\\"]'\"")

if __name__ == "__main__":
    print("🎯 Philips Internal GitHub Access Test")
    print("=" * 50)
    
    access_ok = simple_philips_test()
    
    if access_ok:
        print("\n✅ Ready to collect Philips metrics!")
        configure_philips_variables()
        print("\n🚀 Next steps:")
        print("   1. python view_philips_metrics.py --trigger")
        print("   2. Monitor: http://localhost:8080/dags/philips_github_metrics")
        print("   3. View results: python view_philips_metrics.py")
    else:
        print("\n❌ Access issues detected")
        print("\n🔧 Troubleshooting steps:")
        print("   1. Verify you're a member of philips-internal organization")
        print("   2. Check your GitHub token has these scopes:")
        print("      - repo (for private repository access)")
        print("      - read:org (for organization data)")
        print("      - read:user (for user information)")
        print("   3. Generate a new token if needed:")
        print("      https://github.com/settings/tokens")
        print("   4. Update Airflow variable:")
        print("      wsl bash -c \"source ~/airflow-venv/bin/activate && airflow variables set GITHUB_TOKEN 'your_new_token'\"")
