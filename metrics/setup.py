#!/usr/bin/env python3
"""
Setup script for GitHub Metrics Collection System
"""

import os
import sys
import subprocess
import json
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True


def install_dependencies():
    """Install required Python packages."""
    print("📦 Installing dependencies...")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False


def setup_environment():
    """Setup environment configuration."""
    print("🔧 Setting up environment...")
    
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists() and env_example.exists():
        # Copy example env file
        with open(env_example, 'r') as src, open(env_file, 'w') as dst:
            dst.write(src.read())
        print("✅ Created .env file from example")
        print("⚠️  Please edit .env file with your GitHub token and repositories")
    elif env_file.exists():
        print("✅ .env file already exists")
    else:
        print("⚠️  No .env.example file found")
    
    return True


def setup_output_directory():
    """Create output directory structure."""
    print("📁 Setting up output directories...")
    
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    (output_dir / "charts").mkdir(exist_ok=True)
    (output_dir / "reports").mkdir(exist_ok=True)
    
    print("✅ Output directories created")
    return True


def validate_github_token():
    """Validate GitHub token if provided."""
    token = os.getenv('GITHUB_TOKEN') or os.getenv('METRICS_GITHUB_TOKEN')
    
    if not token:
        print("⚠️  No GitHub token found in environment")
        print("   Please set GITHUB_TOKEN or METRICS_GITHUB_TOKEN environment variable")
        return False
    
    try:
        # Try to import and test GitHub connection
        sys.path.insert(0, 'github_metrics')
        from config import validate_github_token_scopes
        
        result = validate_github_token_scopes(token)
        
        if result['valid']:
            print(f"✅ GitHub token valid for user: {result['user']}")
            print(f"   Rate limit remaining: {result['rate_limit_remaining']}")
            return True
        else:
            print(f"❌ GitHub token validation failed: {result['message']}")
            return False
            
    except ImportError:
        print("⚠️  Cannot validate GitHub token (PyGithub not installed)")
        return False
    except Exception as e:
        print(f"❌ Error validating GitHub token: {e}")
        return False


def create_sample_config():
    """Create sample Airflow configuration."""
    print("⚙️  Creating sample Airflow configuration...")
    
    airflow_vars = {
        "GITHUB_TOKEN": "your_github_token_here",
        "GITHUB_REPOSITORIES": ["microsoft/vscode", "facebook/react"],
        "METRICS_COLLECTION_DAYS": 30,
        "METRICS_OUTPUT_DIR": "./output"
    }
    
    config_file = Path("airflow_variables.json")
    with open(config_file, 'w') as f:
        json.dump(airflow_vars, f, indent=2)
    
    print(f"✅ Sample Airflow configuration saved to {config_file}")
    print("   Import with: airflow variables import airflow_variables.json")
    
    return True


def run_test():
    """Run basic functionality test."""
    print("🧪 Running basic functionality test...")
    
    try:
        # Run the test script
        result = subprocess.run([
            sys.executable, "test_metrics.py"
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ Basic functionality test passed")
            return True
        else:
            print("❌ Basic functionality test failed")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("⚠️  Test timed out (this is normal if no GitHub token is configured)")
        return False
    except Exception as e:
        print(f"❌ Error running test: {e}")
        return False


def print_next_steps():
    """Print next steps for the user."""
    print("\n" + "="*50)
    print("🎉 Setup Complete!")
    print("="*50)
    
    print("\nNext Steps:")
    print("1. Configure your GitHub token:")
    print("   - Edit .env file with your GitHub Personal Access Token")
    print("   - Or set GITHUB_TOKEN environment variable")
    
    print("\n2. Configure repositories:")
    print("   - Edit METRICS_GITHUB_REPOSITORIES in .env file")
    print("   - Or update airflow_variables.json")
    
    print("\n3. Test the setup:")
    print("   python test_metrics.py")
    
    print("\n4. For Airflow deployment:")
    print("   - Copy dags/github_metrics_dag.py to your Airflow DAGs folder")
    print("   - Copy github_metrics/ package to your Airflow DAGs folder")
    print("   - Import variables: airflow variables import airflow_variables.json")
    
    print("\n5. Run the dashboard:")
    print("   python -c \"from github_metrics.dashboard import MetricsDashboard; dashboard = MetricsDashboard({}); dashboard.run()\"")
    
    print("\nDocumentation:")
    print("   - See README.md for detailed usage instructions")
    print("   - Check .github/copilot-instructions.md for development guidelines")


def main():
    """Main setup function."""
    print("🚀 GitHub Metrics Collection System Setup")
    print("="*50)
    
    steps = [
        ("Checking Python version", check_python_version),
        ("Installing dependencies", install_dependencies),
        ("Setting up environment", setup_environment),
        ("Setting up output directories", setup_output_directory),
        ("Creating sample configuration", create_sample_config),
        ("Validating GitHub token", validate_github_token),
    ]
    
    failed_steps = []
    
    for step_name, step_func in steps:
        print(f"\n{step_name}...")
        try:
            if not step_func():
                failed_steps.append(step_name)
        except Exception as e:
            print(f"❌ Error in {step_name}: {e}")
            failed_steps.append(step_name)
    
    # Optional test
    print(f"\nOptional test...")
    run_test()
    
    print_next_steps()
    
    if failed_steps:
        print(f"\n⚠️  Some steps failed: {', '.join(failed_steps)}")
        print("Please review the errors above and fix them before proceeding.")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
