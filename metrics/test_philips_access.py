#!/usr/bin/env python3
"""
Test access to Philips Internal organization and team
"""

from github import Github
import subprocess
import json

def test_philips_access():
    """Test access to Philips Internal organization."""
    try:
        # Get GitHub token from Airflow
        result = subprocess.run(['wsl', 'bash', '-c', 'source ~/airflow-venv/bin/activate && airflow variables get GITHUB_TOKEN'], 
                              capture_output=True, text=True)
        token = result.stdout.strip()
        
        if not token:
            print("❌ No GitHub token found in Airflow variables")
            return
        
        g = Github(token)
        
        # Test organization access
        print("🔍 Testing Philips Internal organization access...")
        try:
            org = g.get_organization('philips-internal')
            print(f"✅ Access confirmed to: {org.name or 'philips-internal'}")
            print(f"   📊 Public repos: {org.public_repos}")
            print(f"   🔒 Private repos: {org.total_private_repos}")
            print(f"   👥 Total members: {org.get_members().totalCount}")
            
            # List some repositories
            print(f"\n📦 Sample repositories:")
            repos = list(org.get_repos()[:10])  # Get first 10 repos
            for i, repo in enumerate(repos, 1):
                print(f"   {i}. {repo.full_name} ({repo.language or 'Unknown'}) - {repo.stargazers_count}⭐")
            
            if len(repos) >= 10:
                print(f"   ... and {org.public_repos + org.total_private_repos - 10} more repositories")
            
            return True
            
        except Exception as org_error:
            print(f"❌ Cannot access philips-internal organization: {org_error}")
            print("   This might be because:")
            print("   - Your token doesn't have org access permissions")
            print("   - You're not a member of the organization")
            print("   - The organization name is different")
            return False
            
    except Exception as e:
        print(f"❌ General error: {e}")
        return False

def test_team_access():
    """Test access to specific team members."""
    try:
        result = subprocess.run(['wsl', 'bash', '-c', 'source ~/airflow-venv/bin/activate && airflow variables get GITHUB_TOKEN'], 
                              capture_output=True, text=True)
        token = result.stdout.strip()
        g = Github(token)
        
        print(f"\n👥 Testing team access...")
        try:
            org = g.get_organization('philips-internal')
            
            # Try to get team information
            try:
                team = org.get_team_by_slug('hpm-synergy-blr')
                print(f"✅ Found team: {team.name}")
                print(f"   👥 Team members: {team.members_count}")
                
                # List team members
                members = list(team.get_members())
                print(f"   📋 Team members:")
                for member in members[:10]:  # Show first 10 members
                    print(f"      - {member.login} ({member.name or 'No name'})")
                
                if len(members) > 10:
                    print(f"      ... and {len(members) - 10} more members")
                
                return members
                
            except Exception as team_error:
                print(f"⚠️  Cannot access team 'hpm-synergy-blr': {team_error}")
                print("   This might be because:")
                print("   - Team is private and you don't have access")
                print("   - Team name/slug is different")
                print("   - Token doesn't have team read permissions")
                
                # Try to list all teams you can see
                print(f"\n   🔍 Listing accessible teams:")
                try:
                    teams = list(org.get_teams())
                    if teams:
                        for team in teams[:5]:
                            print(f"      - {team.slug} ({team.name})")
                    else:
                        print("      No teams accessible")
                except:
                    print("      Cannot list teams")
                
                return None
                
        except Exception as org_error:
            print(f"❌ Organization access error: {org_error}")
            return None
            
    except Exception as e:
        print(f"❌ Team access error: {e}")
        return None

def suggest_repositories():
    """Suggest which repositories to monitor based on team activity."""
    try:
        result = subprocess.run(['wsl', 'bash', '-c', 'source ~/airflow-venv/bin/activate && airflow variables get GITHUB_TOKEN'], 
                              capture_output=True, text=True)
        token = result.stdout.strip()
        g = Github(token)
        
        print(f"\n📊 Repository recommendations:")
        
        org = g.get_organization('philips-internal')
        repos = list(org.get_repos(sort='updated', direction='desc')[:20])  # Most recently updated
        
        print(f"   🔥 Most active repositories (last 20):")
        for i, repo in enumerate(repos, 1):
            last_update = repo.updated_at.strftime('%Y-%m-%d') if repo.updated_at else 'Unknown'
            print(f"   {i:2d}. {repo.full_name}")
            print(f"       📅 Updated: {last_update} | 💻 {repo.language or 'Unknown'} | ⭐ {repo.stargazers_count}")
        
        return [repo.full_name for repo in repos]
        
    except Exception as e:
        print(f"❌ Repository suggestion error: {e}")
        return []

if __name__ == "__main__":
    print("🔍 Philips Internal GitHub Access Test")
    print("=" * 50)
    
    # Test organization access
    org_access = test_philips_access()
    
    # Test team access
    team_members = test_team_access()
    
    # Suggest repositories
    suggested_repos = suggest_repositories()
    
    print(f"\n📋 Summary:")
    print(f"   Organization Access: {'✅' if org_access else '❌'}")
    print(f"   Team Access: {'✅' if team_members else '❌'}")
    print(f"   Suggested Repos: {len(suggested_repos)}")
    
    if org_access and suggested_repos:
        print(f"\n🚀 Recommended next steps:")
        print(f"   1. Update Airflow variables with Philips repos")
        print(f"   2. Configure team member filtering")
        print(f"   3. Run enhanced DAG for DORA metrics")
