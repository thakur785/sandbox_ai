#!/usr/bin/env python3
"""
GitHub Token Setup Helper - Solve Rate Limit Issues
"""

import os

def show_rate_limit_info():
    """Explain GitHub rate limits and solutions."""
    print("🚫 GitHub API Rate Limit Explained")
    print("=" * 40)
    print()
    print("📊 Rate Limits:")
    print("   • Without token: 60 requests/hour")
    print("   • With token: 5,000 requests/hour")
    print()
    print("⏰ When you see 'rate limit exceeded':")
    print("   • GitHub temporarily blocks your requests")
    print("   • You must wait ~30 minutes, OR")
    print("   • Use a GitHub Personal Access Token")
    print()

def show_token_setup():
    """Show how to create and use a GitHub token."""
    print("🔑 How to Create a GitHub Token")
    print("=" * 35)
    print()
    print("1. 🌐 Go to: https://github.com/settings/tokens")
    print("2. 🔘 Click 'Generate new token (classic)'")
    print("3. 📝 Name: 'GitHub Metrics Collection'")
    print("4. ☑️  Select scopes:")
    print("   ☑️  repo (Full control of repositories)")
    print("   ☑️  read:org (Read org membership)")
    print("   ☑️  read:user (Read user profile)")
    print("5. 🔄 Click 'Generate token'")
    print("6. 📋 Copy the token (you won't see it again!)")
    print()

def show_usage_options():
    """Show different ways to use the token."""
    print("💾 How to Use Your Token")
    print("=" * 25)
    print()
    print("Option 1 - Environment Variable (Recommended):")
    if os.name == 'nt':  # Windows
        print("   set GITHUB_TOKEN=your_token_here")
        print("   python simple_test_enhanced.py")
    else:
        print("   export GITHUB_TOKEN=your_token_here")
        print("   python simple_test_enhanced.py")
    print()
    print("Option 2 - .env File:")
    print("   Create .env file with:")
    print("   GITHUB_TOKEN=your_token_here")
    print()
    print("Option 3 - Temporarily in Script:")
    print("   Edit simple_test_enhanced.py:")
    print("   os.environ['GITHUB_TOKEN'] = 'your_token_here'")
    print()

def create_env_template():
    """Create a .env template file."""
    env_content = """# GitHub Metrics Configuration
# Replace 'your_token_here' with your actual GitHub Personal Access Token

GITHUB_TOKEN=your_token_here
METRICS_GITHUB_TOKEN=your_token_here

# Optional: Specify repositories (comma-separated)
METRICS_GITHUB_REPOSITORIES=microsoft/vscode,facebook/react,vercel/next.js

# Optional: Specify users to track (comma-separated)
METRICS_TRACKED_USERS=gaearon,timneutkens,jrieken,alexdima

# Optional: Specify email domains to track
METRICS_TRACKED_EMAIL_DOMAINS=microsoft.com,facebook.com
"""
    
    try:
        with open('.env.template', 'w') as f:
            f.write(env_content)
        print("✅ Created .env.template file")
        print("   1. Copy .env.template to .env")
        print("   2. Edit .env and add your GitHub token")
    except Exception as e:
        print(f"❌ Failed to create template: {e}")

def check_current_setup():
    """Check if token is already configured."""
    print("🔍 Current Setup Check")
    print("=" * 25)
    
    token = os.getenv('GITHUB_TOKEN') or os.getenv('METRICS_GITHUB_TOKEN')
    
    if token:
        masked_token = token[:8] + "..." + token[-4:] if len(token) > 12 else "***"
        print(f"✅ Token found: {masked_token}")
        print("   Your rate limit should be 5,000/hour")
    else:
        print("❌ No token found")
        print("   Current rate limit: 60/hour (very limited)")
    
    # Check for .env file
    if os.path.exists('.env'):
        print("✅ .env file exists")
    else:
        print("⚠️  No .env file found")

def main():
    """Main function to guide through rate limit resolution."""
    print("🚀 GitHub Rate Limit Resolver")
    print("=" * 35)
    print()
    
    # Check current setup
    check_current_setup()
    print()
    
    # Show rate limit info
    show_rate_limit_info()
    
    # Show token setup
    show_token_setup()
    
    # Show usage options
    show_usage_options()
    
    # Create template
    print("📁 Creating Configuration Template")
    print("=" * 35)
    create_env_template()
    
    print()
    print("🎯 Quick Fix Summary:")
    print("1. Create GitHub token (5 minutes)")
    print("2. Set GITHUB_TOKEN environment variable")
    print("3. Re-run your script")
    print("4. Enjoy 5,000 requests/hour instead of 60!")

if __name__ == "__main__":
    main()
