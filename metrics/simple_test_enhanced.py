#!/usr/bin/env python3
"""
Simple GitHub Metrics Test with Hardcoded Configuration
"""

import os
from datetime import datetime, timedelta
from github import Github
import json

# Try to import our custom modules, but continue if they fail
try:
    from github_metrics.collectors import GitHubCollector
    from github_metrics.metrics import DORAMetrics, PRMetrics, ProductivityMetrics
    MODULES_AVAILABLE = True
    print("✅ GitHub metrics modules loaded successfully")
except ImportError as e:
    print(f"⚠️  GitHub metrics modules not available: {e}")
    print("   Running in basic mode with limited functionality")
    MODULES_AVAILABLE = False
    GitHubCollector = None
    DORAMetrics = None
    PRMetrics = None
    ProductivityMetrics = None

# 🔧 HARDCODED CONFIGURATION
# =========================

# GitHub repositories to analyze (add your repos here)
REPOSITORIES = [
    "microsoft/vscode",          # Large open source project
    "facebook/react",            # Popular frontend framework
    "vercel/next.js",           # Next.js framework
    # "your-org/your-repo",      # Add your repositories here
]

# User groups for filtering metrics (add your team members here)
USER_GROUPS = {
    "frontend_team": [
        "gaearon",              # Dan Abramov (React)
        "sebmarkbage",          # Sebastian Markbage
        "acdlite",              # Andrew Clark
    ],
    "core_team": [
        "timneutkens",          # Tim Neutkens (Next.js)
        "ijjk",                 # JJ Kasper
        "styfle",               # Steven Tey
    ],
    "vscode_team": [
        "jrieken",              # Johannes Rieken
        "alexdima",             # Alex Dima
        "bpasero",              # Benjamin Pasero
    ],
    # Add your teams here:
    "my_team": [
        # "john.doe",
        # "jane.smith", 
        # "dev.lead",
    ]
}

# Collection settings
DAYS_TO_ANALYZE = 30
ENVIRONMENT = "development"  # Options: development, staging, production


def get_github_token():
    """Get GitHub token from environment or use unauthenticated."""
    token = os.getenv('GITHUB_TOKEN') or os.getenv('METRICS_GITHUB_TOKEN')
    if not token:
        print("⚠️  No GitHub token found. Using unauthenticated access (limited rate).")
        print("   📝 Unauthenticated: 60 requests/hour")
        print("   🔑 With token: 5,000 requests/hour")
        print("   💡 Run 'python fix_rate_limit.py' for setup help")
    else:
        print("✅ GitHub token found. Using authenticated access (5,000 requests/hour)")
    return token


def test_simple_metrics():
    """Test basic metrics collection with hardcoded settings."""
    print("🚀 GitHub Metrics - Simple Test")
    print("=" * 50)
    
    # Initialize GitHub connection
    token = get_github_token()
    
    try:
        if token and MODULES_AVAILABLE:
            collector = GitHubCollector(token)
            print("✅ Authenticated GitHub connection established")
        else:
            g = Github(token) if token else Github()  # Use token if available
            connection_type = "authenticated" if token else "unauthenticated"
            print(f"✅ {connection_type.title()} GitHub connection established")
            
        # Test with first repository
        test_repo = REPOSITORIES[0]
        print(f"📂 Testing with repository: {test_repo}")
        
        if token and MODULES_AVAILABLE:
            # Full metrics collection with authentication
            since_date = datetime.now() - timedelta(days=DAYS_TO_ANALYZE)
            
            print(f"📅 Collecting data from {since_date.strftime('%Y-%m-%d')} to now...")
            
            # Collect data for specific user group
            user_filter = USER_GROUPS.get("vscode_team", [])  # Use vscode team for microsoft/vscode
            if test_repo == "facebook/react":
                user_filter = USER_GROUPS.get("frontend_team", [])
            elif test_repo == "vercel/next.js":
                user_filter = USER_GROUPS.get("core_team", [])
            
            print(f"👥 Filtering for users: {', '.join(user_filter) if user_filter else 'All users'}")
            
            # Collect all data
            all_data = collector.collect_all_data(
                repo_name=test_repo,
                since=since_date,
                user_filter=user_filter if user_filter else None
            )
            
            # Calculate metrics
            print("\n📊 CALCULATING METRICS")
            print("=" * 25)
            
            # DORA Metrics
            dora_calculator = DORAMetrics(all_data)
            dora_metrics = dora_calculator.get_all_dora_metrics(period_days=DAYS_TO_ANALYZE)
            
            print("🎯 DORA Metrics:")
            print(f"   📈 Deployment Frequency: {dora_metrics['deployment_frequency']['deployments_per_week']:.1f}/week")
            print(f"   ⏱️  Lead Time: {dora_metrics['lead_time_for_changes']['median_lead_time_hours']:.1f}h (median)")
            print(f"   🔧 MTTR: {dora_metrics['mean_time_to_recovery']['median_recovery_time_hours']:.1f}h (median)")
            print(f"   💥 Change Failure Rate: {dora_metrics['change_failure_rate']['change_failure_rate']:.1%}")
            
            # PR Metrics
            pr_calculator = PRMetrics(all_data)
            pr_metrics = pr_calculator.get_all_pr_metrics()
            
            print("\n📋 Pull Request Metrics:")
            print(f"   ⏰ Avg Cycle Time: {pr_metrics['cycle_time_analysis']['mean_cycle_time_hours']:.1f}h")
            print(f"   📝 Avg Review Comments: {pr_metrics['review_analysis']['mean_review_comments']:.1f}")
            print(f"   ✅ Merge Rate: {pr_metrics['merge_analysis']['merge_rate']:.1%}")
            print(f"   📊 Total PRs: {pr_metrics['merge_analysis']['total_prs']}")
            
            # Productivity Metrics
            prod_calculator = ProductivityMetrics(all_data)
            prod_metrics = prod_calculator.get_all_productivity_metrics()
            
            print("\n🏆 Productivity Metrics:")
            print(f"   👨‍💻 Active Developers: {prod_metrics['developer_activity']['commit_activity']['total_authors']}")
            print(f"   📝 Total Commits: {prod_metrics['developer_activity']['commit_activity']['total_commits']}")
            print(f"   🤝 Collaboration Pairs: {prod_metrics['collaboration_metrics']['collaboration_pairs']}")
            
            # Save sample results
            sample_data = {
                "timestamp": datetime.now().isoformat(),
                "repository": test_repo,
                "user_filter": user_filter,
                "collection_period_days": DAYS_TO_ANALYZE,
                "dora_metrics": dora_metrics,
                "pr_metrics": pr_metrics,
                "productivity_metrics": prod_metrics,
                "data_summary": {
                    "pull_requests": len(all_data['pull_requests']),
                    "commits": len(all_data['commits']),
                    "issues": len(all_data['issues']),
                    "deployments": len(all_data['deployments'])
                }
            }
            
            with open('sample_metrics_results.json', 'w') as f:
                json.dump(sample_data, f, indent=2, default=str)
            
            print(f"\n💾 Results saved to: sample_metrics_results.json")
            
        else:
            # Basic test without advanced modules
            g = Github(token) if token else Github()
            repo = g.get_repo(test_repo)
            
            print(f"✅ Repository: {repo.name}")
            print(f"📝 Description: {repo.description}")
            print(f"⭐ Stars: {repo.stargazers_count}")
            print(f"🍴 Forks: {repo.forks_count}")
            print(f"🐛 Open Issues: {repo.open_issues_count}")
            
            # Enhanced basic PR analysis
            print(f"\n📊 Enhanced Analysis:")
            prs = list(repo.get_pulls(state='all')[:50])  # Get more PRs for better analysis
            merged_prs = [pr for pr in prs if pr.merged]
            open_prs = [pr for pr in prs if pr.state == 'open']
            closed_prs = [pr for pr in prs if pr.state == 'closed' and not pr.merged]
            
            print(f"   📋 Recent PRs analyzed: {len(prs)}")
            print(f"   ✅ Merged: {len(merged_prs)} ({len(merged_prs)/len(prs)*100:.1f}%)")
            print(f"   � Open: {len(open_prs)} ({len(open_prs)/len(prs)*100:.1f}%)")
            print(f"   ❌ Closed (not merged): {len(closed_prs)} ({len(closed_prs)/len(prs)*100:.1f}%)")
            
            # User filtering demo
            target_users = USER_GROUPS.get("vscode_team", [])
            if test_repo == "facebook/react":
                target_users = USER_GROUPS.get("frontend_team", [])
            elif test_repo == "vercel/next.js":
                target_users = USER_GROUPS.get("core_team", [])
            
            if target_users:
                print(f"\n👥 Filtering for team users: {', '.join(target_users)}")
                user_prs = [pr for pr in prs if pr.user and pr.user.login in target_users]
                print(f"   📋 PRs by team members: {len(user_prs)}")
                if user_prs:
                    team_merged = [pr for pr in user_prs if pr.merged]
                    print(f"   ✅ Team merge rate: {len(team_merged)/len(user_prs)*100:.1f}%")
            
            # Cycle time analysis
            if merged_prs:
                cycle_times = []
                for pr in merged_prs:
                    if pr.merged_at and pr.created_at:
                        hours = (pr.merged_at - pr.created_at).total_seconds() / 3600
                        cycle_times.append(hours)
                
                if cycle_times:
                    avg_cycle = sum(cycle_times) / len(cycle_times)
                    min_cycle = min(cycle_times)
                    max_cycle = max(cycle_times)
                    print(f"\n⏱️  Cycle Time Analysis:")
                    print(f"   Average: {avg_cycle:.1f}h")
                    print(f"   Fastest: {min_cycle:.1f}h")
                    print(f"   Slowest: {max_cycle:.1f}h")
                    
                    # Basic categorization
                    fast_prs = [t for t in cycle_times if t < 24]
                    medium_prs = [t for t in cycle_times if 24 <= t <= 168]  # 1-7 days
                    slow_prs = [t for t in cycle_times if t > 168]
                    
                    print(f"   🟢 Fast (<24h): {len(fast_prs)} ({len(fast_prs)/len(cycle_times)*100:.1f}%)")
                    print(f"   🟡 Medium (1-7d): {len(medium_prs)} ({len(medium_prs)/len(cycle_times)*100:.1f}%)")
                    print(f"   🔴 Slow (>7d): {len(slow_prs)} ({len(slow_prs)/len(cycle_times)*100:.1f}%)")
            
            # Basic recent activity
            print(f"\n📈 Recent Activity:")
            commits = list(repo.get_commits()[:20])
            print(f"   📝 Recent commits: {len(commits)}")
            
            if commits:
                commit_authors = set()
                for commit in commits:
                    if commit.author:
                        commit_authors.add(commit.author.login)
                print(f"   👨‍💻 Active contributors: {len(commit_authors)}")
                
                if target_users:
                    team_commits = [c for c in commits if c.author and c.author.login in target_users]
                    print(f"   📝 Team commits: {len(team_commits)}")
        
        print("\n✅ SUCCESS! Simple metrics test completed.")
        
        if not MODULES_AVAILABLE:
            print("\n💡 For advanced metrics:")
            print("1. Fix the GitHubCollector import issue")
            print("2. Install missing dependencies: pip install -r requirements.txt")
            print("3. Set up a GitHub token for better rate limits")
            
        return True
        
    except Exception as e:
        error_msg = str(e).lower()
        
        if "rate limit" in error_msg or "403" in error_msg:
            print(f"🚫 GitHub Rate Limit Exceeded!")
            print("=" * 35)
            print("📊 What happened:")
            print("   • You've used up your GitHub API requests")
            print("   • Without token: 60 requests/hour limit")
            print("   • With token: 5,000 requests/hour limit")
            print()
            print("⚡ Quick Solutions:")
            print("1. 🔑 Get a GitHub token (recommended):")
            print("   Run: python fix_rate_limit.py")
            print()
            print("2. ⏰ Wait ~30 minutes for reset")
            print()
            print("3. 🔧 Use basic test instead:")
            print("   python simple_test.py")
            print()
            return False
        else:
            print(f"❌ Error: {e}")
            print("\n💡 Solutions:")
            print("1. Check repository names in REPOSITORIES list")
            print("2. Verify GitHub token if using authenticated access")
            print("3. Check internet connection")
            print("4. For rate limits, run: python fix_rate_limit.py")
            return False


def show_configuration():
    """Display current hardcoded configuration."""
    print("\n🔧 CURRENT CONFIGURATION")
    print("=" * 30)
    
    # Show module availability
    if MODULES_AVAILABLE:
        print("✅ GitHub metrics modules: Available")
    else:
        print("⚠️  GitHub metrics modules: Not available (running in basic mode)")
    
    print("📂 Repositories:")
    for i, repo in enumerate(REPOSITORIES, 1):
        print(f"   {i}. {repo}")
    
    print("\n👥 User Groups:")
    for group_name, users in USER_GROUPS.items():
        print(f"   {group_name}: {len(users)} users")
        for user in users[:3]:  # Show first 3 users
            print(f"      - {user}")
        if len(users) > 3:
            print(f"      ... and {len(users)-3} more")
    
    print(f"\n📅 Analysis Period: {DAYS_TO_ANALYZE} days")
    print(f"🌍 Environment: {ENVIRONMENT}")


def customize_configuration():
    """Show how to customize the hardcoded configuration."""
    print("\n✏️  CUSTOMIZATION GUIDE")
    print("=" * 25)
    print("To customize this script for your organization:")
    print()
    print("1. 📂 Edit REPOSITORIES list:")
    print('   REPOSITORIES = [')
    print('       "your-org/repo1",')
    print('       "your-org/repo2",')
    print('   ]')
    print()
    print("2. 👥 Edit USER_GROUPS dictionary:")
    print('   USER_GROUPS = {')
    print('       "my_team": [')
    print('           "john.doe",')
    print('           "jane.smith",')
    print('       ]')
    print('   }')
    print()
    print("3. ⚙️  Edit settings:")
    print(f'   DAYS_TO_ANALYZE = {DAYS_TO_ANALYZE}  # Change analysis period')
    print()
    print("4. 🔑 Set up GitHub token:")
    print('   export GITHUB_TOKEN="your_token_here"')
    print()


if __name__ == "__main__":
    show_configuration()
    success = test_simple_metrics()
    
    if success:
        customize_configuration()
    
    exit(0 if success else 1)
