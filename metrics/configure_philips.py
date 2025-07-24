#!/usr/bin/env python3
"""
Philips GitHub Metrics Configuration
Configure specific repositories and team members for analysis
"""

import subprocess
import json
import sys

def discover_philips_repositories():
    """Discover available repositories in philips-internal organization."""
    
    print("🔍 Discovering Philips Internal Repositories...")
    print("-" * 50)
    
    discovery_script = """
from github import Github
import subprocess

# Get token
result = subprocess.run(['airflow', 'variables', 'get', 'GITHUB_TOKEN'], capture_output=True, text=True)
token = result.stdout.strip()

g = Github(token)
org = g.get_organization('philips-internal')

print(f'📊 Organization: {org.name or "philips-internal"}')
print(f'   Total repositories: {org.public_repos + org.total_private_repos}')

# Get repositories by activity
repos_by_activity = []
repos_by_language = {}
repos_by_team = []

print('\\n📦 Most Recently Updated Repositories:')
for i, repo in enumerate(org.get_repos(sort='updated', direction='desc')):
    if i >= 20:  # Limit to top 20
        break
    
    repos_by_activity.append({
        'name': repo.full_name,
        'language': repo.language,
        'stars': repo.stargazers_count,
        'forks': repo.forks_count,
        'issues': repo.open_issues_count,
        'updated': repo.updated_at.strftime('%Y-%m-%d'),
        'private': repo.private
    })
    
    # Track languages
    if repo.language:
        if repo.language not in repos_by_language:
            repos_by_language[repo.language] = []
        repos_by_language[repo.language].append(repo.full_name)
    
    print(f'   {i+1:2d}. {repo.full_name}')
    print(f'       💻 {repo.language or "Unknown"} | ⭐ {repo.stargazers_count} | 🐛 {repo.open_issues_count} | 📅 {repo.updated_at.strftime("%Y-%m-%d")}')

print('\\n💻 Repositories by Language:')
for lang, repos in sorted(repos_by_language.items()):
    print(f'   {lang}: {len(repos)} repos')
    for repo in repos[:3]:  # Show first 3
        print(f'      - {repo}')
    if len(repos) > 3:
        print(f'      ... and {len(repos) - 3} more')

# Look for repositories that might be related to the team
print('\\n🔍 Searching for team-related repositories...')
team_keywords = ['synergy', 'hpm', 'healthcare', 'medical', 'platform', 'service']
potential_team_repos = []

for repo in org.get_repos():
    repo_name_lower = repo.name.lower()
    if any(keyword in repo_name_lower for keyword in team_keywords):
        potential_team_repos.append(repo.full_name)
        print(f'   🎯 {repo.full_name} (matches: {[k for k in team_keywords if k in repo_name_lower]})')

# Generate configuration suggestions
print('\\n🚀 Configuration Suggestions:')
print('\\n   Top 5 Most Active Repos:')
for repo in repos_by_activity[:5]:
    print(f'      "{repo["name"]}"')

if potential_team_repos:
    print('\\n   Team-Related Repos:')
    for repo in potential_team_repos[:5]:
        print(f'      "{repo}"')

print(f'\\n📋 JSON Configuration for Airflow:')
config_repos = [repo['name'] for repo in repos_by_activity[:10]]
print(json.dumps(config_repos, indent=2))
"""
    
    try:
        result = subprocess.run([
            'wsl', 'bash', '-c', 
            f'source ~/airflow-venv/bin/activate && python3 -c "{discovery_script}"'
        ], capture_output=True, text=True, timeout=120)
        
        print(result.stdout)
        
        if result.stderr:
            print(f"⚠️  Warnings: {result.stderr}")
        
        if result.returncode != 0:
            print("❌ Repository discovery failed")
            return []
        
        # Extract repository list from output
        lines = result.stdout.split('\n')
        repos = []
        for line in lines:
            if '. philips-internal/' in line:
                repo_name = line.split('. ')[1].split()[0]
                repos.append(repo_name)
        
        return repos
        
    except Exception as e:
        print(f"❌ Discovery failed: {e}")
        return []

def discover_team_members():
    """Discover hpm-synergy-blr team members."""
    
    print("\n👥 Discovering Team Members...")
    print("-" * 40)
    
    team_script = """
from github import Github
import subprocess

# Get token
result = subprocess.run(['airflow', 'variables', 'get', 'GITHUB_TOKEN'], capture_output=True, text=True)
token = result.stdout.strip()

g = Github(token)
org = g.get_organization('philips-internal')

try:
    team = org.get_team_by_slug('hpm-synergy-blr')
    print(f'✅ Team: {team.name}')
    print(f'   Members: {team.members_count}')
    print(f'   Privacy: {team.privacy}')
    print(f'   Description: {team.description or "No description"}')
    
    print('\\n👥 Team Members:')
    members = []
    for i, member in enumerate(team.get_members()):
        members.append({
            'login': member.login,
            'name': member.name,
            'company': member.company,
            'location': member.location
        })
        print(f'   {i+1:2d}. {member.login} ({member.name or "No name"})')
        if member.company:
            print(f'       🏢 {member.company}')
        if member.location:
            print(f'       📍 {member.location}')
    
    print(f'\\n📋 Team Member Logins for Configuration:')
    logins = [m['login'] for m in members]
    print(json.dumps(logins, indent=2))
    
except Exception as e:
    print(f'❌ Team access denied: {str(e)[:100]}')
    print('   Possible reasons:')
    print('   - Team is private and you don\\'t have access')
    print('   - Team slug might be different')
    print('   - Token lacks team read permissions')
    
    print('\\n🔍 Trying to list accessible teams...')
    try:
        teams = list(org.get_teams())
        if teams:
            print(f'   Found {len(teams)} accessible teams:')
            for team in teams[:10]:
                print(f'      - {team.slug} ({team.name})')
        else:
            print('   No teams accessible with current permissions')
    except:
        print('   Cannot list teams')
"""
    
    try:
        result = subprocess.run([
            'wsl', 'bash', '-c', 
            f'source ~/airflow-venv/bin/activate && python3 -c "{team_script}"'
        ], capture_output=True, text=True, timeout=60)
        
        print(result.stdout)
        
        if result.stderr:
            print(f"⚠️  Warnings: {result.stderr}")
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Team discovery failed: {e}")
        return False

def configure_airflow_variables(repositories=None, team_members=None):
    """Configure Airflow variables for Philips metrics collection."""
    
    print("\n🔧 Configuring Airflow Variables...")
    print("-" * 40)
    
    if repositories:
        print(f"📦 Setting PHILIPS_REPOSITORIES with {len(repositories)} repos...")
        repos_json = json.dumps(repositories)
        
        try:
            result = subprocess.run([
                'wsl', 'bash', '-c', 
                f'source ~/airflow-venv/bin/activate && airflow variables set PHILIPS_REPOSITORIES \'{repos_json}\''
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ PHILIPS_REPOSITORIES configured")
            else:
                print(f"❌ Failed to set repositories: {result.stderr}")
        except Exception as e:
            print(f"❌ Variable configuration failed: {e}")
    
    if team_members:
        print(f"👥 Setting PHILIPS_TEAM_MEMBERS with {len(team_members)} members...")
        members_json = json.dumps(team_members)
        
        try:
            result = subprocess.run([
                'wsl', 'bash', '-c', 
                f'source ~/airflow-venv/bin/activate && airflow variables set PHILIPS_TEAM_MEMBERS \'{members_json}\''
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ PHILIPS_TEAM_MEMBERS configured")
            else:
                print(f"❌ Failed to set team members: {result.stderr}")
        except Exception as e:
            print(f"❌ Team variable configuration failed: {e}")
    
    # Set other useful variables
    other_vars = {
        'PHILIPS_COLLECTION_DAYS': '30',
        'PHILIPS_TEAM_SLUG': 'hpm-synergy-blr',
        'PHILIPS_ORG_NAME': 'philips-internal'
    }
    
    for var_name, var_value in other_vars.items():
        try:
            result = subprocess.run([
                'wsl', 'bash', '-c', 
                f'source ~/airflow-venv/bin/activate && airflow variables set {var_name} "{var_value}"'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ {var_name} = {var_value}")
        except:
            print(f"⚠️  Failed to set {var_name}")

def show_configuration_summary():
    """Show current configuration."""
    
    print("\n📋 Current Philips Configuration:")
    print("-" * 40)
    
    variables_to_check = [
        'GITHUB_TOKEN',
        'PHILIPS_REPOSITORIES', 
        'PHILIPS_TEAM_MEMBERS',
        'PHILIPS_COLLECTION_DAYS',
        'PHILIPS_TEAM_SLUG',
        'PHILIPS_ORG_NAME'
    ]
    
    for var_name in variables_to_check:
        try:
            result = subprocess.run([
                'wsl', 'bash', '-c', 
                f'source ~/airflow-venv/bin/activate && airflow variables get {var_name}'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                value = result.stdout.strip()
                if var_name == 'GITHUB_TOKEN':
                    # Don't show the actual token
                    print(f"✅ {var_name}: {'*' * (len(value) - 4) + value[-4:]}")
                elif len(value) > 100:
                    print(f"✅ {var_name}: {value[:50]}... ({len(value)} chars)")
                else:
                    print(f"✅ {var_name}: {value}")
            else:
                print(f"❌ {var_name}: Not set")
        except:
            print(f"❌ {var_name}: Error checking")

if __name__ == "__main__":
    print("🔧 Philips GitHub Metrics Configuration")
    print("=" * 50)
    
    if len(sys.argv) > 1 and sys.argv[1] == "--summary":
        show_configuration_summary()
        sys.exit(0)
    
    # Step 1: Discover repositories
    repositories = discover_philips_repositories()
    
    # Step 2: Discover team members
    team_access = discover_team_members()
    
    # Step 3: Configure variables
    if repositories:
        # Use top 10 most active repositories
        selected_repos = repositories[:10]
        configure_airflow_variables(repositories=selected_repos)
    
    # Step 4: Show summary
    print("\n" + "="*50)
    show_configuration_summary()
    
    print("\n🚀 Next Steps:")
    print("   1. Review the configuration above")
    print("   2. Trigger collection: python view_philips_metrics.py --trigger")
    print("   3. Monitor progress: http://localhost:8080/dags/philips_github_metrics")
    print("   4. View results: python view_philips_metrics.py")
    print("\n💡 To reconfigure: python configure_philips.py")
    print("💡 To see current config: python configure_philips.py --summary")
