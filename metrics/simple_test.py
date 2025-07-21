#!/usr/bin/env python3
"""
Simple GitHub API test script
"""

from github import Github
from datetime import datetime, timedelta
import json


def test_github_api():
    """Test GitHub API access and basic data collection."""
    print("🚀 GitHub Metrics System - Basic Test")
    print("=" * 50)
    
    # Test without authentication first
    print("📡 Testing GitHub API connection...")
    
    try:
        g = Github()  # No authentication - limited rate but works for testing
        
        # Test with the octocat/Hello-World repository (famous test repo)
        repo_name = "octocat/Hello-World"
        print(f"📂 Testing with repository: {repo_name}")
        
        repo = g.get_repo(repo_name)
        
        print(f"✅ Repository access successful!")
        print(f"   Name: {repo.name}")
        print(f"   Description: {repo.description}")
        print(f"   Language: {repo.language}")
        print(f"   Stars: ⭐ {repo.stargazers_count}")
        print(f"   Forks: 🍴 {repo.forks_count}")
        print(f"   Open Issues: 🐛 {repo.open_issues_count}")
        print(f"   Last Updated: {repo.updated_at}")
        print()
        
        # Test pull requests collection
        print("📋 Collecting pull requests...")
        prs = list(repo.get_pulls(state='all')[:10])  # Get last 10 PRs
        print(f"   Found {len(prs)} pull requests")
        
        if prs:
            print("   Recent Pull Requests:")
            for i, pr in enumerate(prs[:3], 1):
                status = "🟢 MERGED" if pr.merged else "🔴 CLOSED" if pr.state == 'closed' else "🟡 OPEN"
                print(f"   {i}. {status} #{pr.number}: {pr.title}")
                print(f"      Created: {pr.created_at}")
                if pr.merged_at:
                    cycle_time = (pr.merged_at - pr.created_at).total_seconds() / 3600
                    print(f"      Cycle Time: {cycle_time:.1f} hours")
        print()
        
        # Test issues collection
        print("🐛 Collecting issues...")
        issues = list(repo.get_issues(state='all')[:5])
        print(f"   Found {len(issues)} recent issues")
        
        if issues:
            print("   Recent Issues:")
            for i, issue in enumerate(issues[:3], 1):
                if not issue.pull_request:  # Skip PRs (they appear as issues too)
                    status = "🟢 CLOSED" if issue.state == 'closed' else "🔴 OPEN"
                    print(f"   {i}. {status} #{issue.number}: {issue.title}")
        print()
        
        # Test commits collection  
        print("📝 Collecting commits...")
        commits = list(repo.get_commits()[:5])
        print(f"   Found {len(commits)} recent commits")
        
        if commits:
            print("   Recent Commits:")
            for i, commit in enumerate(commits[:3], 1):
                message = commit.commit.message.split('\n')[0][:50]
                print(f"   {i}. {commit.sha[:8]}: {message}")
                print(f"      Author: {commit.commit.author.name}")
                print(f"      Date: {commit.commit.author.date}")
        print()
        
        # Calculate some basic metrics
        print("📊 BASIC METRICS CALCULATION")
        print("=" * 30)
        
        if prs:
            merged_prs = [pr for pr in prs if pr.merged]
            open_prs = [pr for pr in prs if pr.state == 'open']
            closed_prs = [pr for pr in prs if pr.state == 'closed' and not pr.merged]
            
            print(f"📈 Pull Request Analysis:")
            print(f"   Total PRs analyzed: {len(prs)}")
            print(f"   ✅ Merged: {len(merged_prs)} ({len(merged_prs)/len(prs)*100:.1f}%)")
            print(f"   🟡 Open: {len(open_prs)} ({len(open_prs)/len(prs)*100:.1f}%)")
            print(f"   ❌ Closed (not merged): {len(closed_prs)} ({len(closed_prs)/len(prs)*100:.1f}%)")
            
            # Calculate cycle times for merged PRs
            cycle_times = []
            for pr in merged_prs:
                if pr.merged_at and pr.created_at:
                    cycle_time = (pr.merged_at - pr.created_at).total_seconds() / 3600
                    cycle_times.append(cycle_time)
            
            if cycle_times:
                avg_cycle_time = sum(cycle_times) / len(cycle_times)
                min_cycle_time = min(cycle_times)
                max_cycle_time = max(cycle_times)
                
                print(f"⏱️  Cycle Time Analysis:")
                print(f"   Average: {avg_cycle_time:.1f} hours")
                print(f"   Fastest: {min_cycle_time:.1f} hours")
                print(f"   Slowest: {max_cycle_time:.1f} hours")
        
        print()
        print("🎉 SUCCESS! GitHub API test completed successfully!")
        print()
        print("📋 What this test demonstrated:")
        print("   ✅ GitHub API connectivity")
        print("   ✅ Repository data access")  
        print("   ✅ Pull requests collection")
        print("   ✅ Issues collection")
        print("   ✅ Commits collection")
        print("   ✅ Basic metrics calculation")
        print()
        
        # Rate limit info
        rate_limit = g.get_rate_limit()
        print(f"📊 API Rate Limit Status:")
        print(f"   Remaining requests: {rate_limit.core.remaining}/{rate_limit.core.limit}")
        print(f"   Reset time: {rate_limit.core.reset}")
        print()
        
        print("🔥 NEXT STEPS:")
        print("1. Get a GitHub Personal Access Token for higher rate limits")
        print("2. Add your token to the .env file")
        print("3. Configure your repositories in .env")
        print("4. Install missing dependencies: pip install plotly dash")
        print("5. Run the full example: python example.py")
        print("6. Start the dashboard: python run_dashboard.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print()
        print("💡 Possible solutions:")
        print("1. Check your internet connection")
        print("2. GitHub API might be rate-limited")
        print("3. Try again in a few minutes")
        print("4. Consider getting a GitHub Personal Access Token")
        
        return False


def show_token_setup():
    """Show how to set up GitHub token."""
    print("\n🔑 GITHUB TOKEN SETUP GUIDE")
    print("=" * 40)
    print("To get higher rate limits and access private repos:")
    print()
    print("1. Go to: https://github.com/settings/tokens")
    print("2. Click 'Generate new token (classic)'")
    print("3. Give it a name: 'GitHub Metrics Collection'")
    print("4. Select scopes:")
    print("   ☑️  repo (Full control of private repositories)")
    print("   ☑️  read:org (Read org and team membership)")
    print("   ☑️  read:user (Read user profile data)")
    print("   ☑️  read:project (Read project data)")
    print("5. Click 'Generate token'")
    print("6. Copy the token (you won't see it again!)")
    print("7. Edit .env file and replace 'your_github_personal_access_token_here'")
    print()


if __name__ == "__main__":
    success = test_github_api()
    
    if success:
        show_token_setup()
    
    exit(0 if success else 1)
