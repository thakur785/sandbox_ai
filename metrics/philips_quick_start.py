#!/usr/bin/env python3
"""
Philips Metrics Collection - Quick Start Guide
"""

import os

def show_philips_quick_start():
    """Show the quick start guide for Philips metrics collection."""
    
    print("🎯 Philips Internal GitHub Metrics - Quick Start")
    print("=" * 60)
    
    print("\n📋 Step-by-Step Guide:")
    print("1️⃣  Test Philips Access:")
    print("    python test_philips_access.py")
    print("    → Verifies access to philips-internal organization")
    print()
    
    print("2️⃣  Test Synergy Repository:")
    print("    python test_synergy_base.py")
    print("    → Tests synergy-base repository and team access")
    print()
    
    print("3️⃣  Configure Variables (Optional):")
    print("    python configure_philips.py")
    print("    → Auto-discovers repositories and configures Airflow")
    print()
    
    print("4️⃣  Trigger Collection:")
    print("    python view_philips_metrics.py --trigger")
    print("    → Starts the metrics collection process")
    print()
    
    print("5️⃣  Monitor Progress:")
    print("    python monitor_synergy_metrics.py")
    print("    → Tracks collection progress and shows results")
    print()
    
    print("6️⃣  View Results:")
    print("    python view_philips_metrics.py")
    print("    → Displays collected metrics and analytics")
    print()
    
    print("🌐 Web Interfaces:")
    print("   Airflow Dashboard: http://localhost:8080/dags/philips_github_metrics")
    print()
    
    print("🎯 Current Configuration:")
    print("   Organization: philips-internal")
    print("   Repository: synergy-base")
    print("   Team: hmp-synergy-blr")
    print()
    
    print("📁 Available Scripts:")
    scripts = [
        ("test_philips_access.py", "Test organization and team access"),
        ("test_synergy_base.py", "Test specific repository access"),
        ("configure_philips.py", "Auto-configure Airflow variables"),
        ("view_philips_metrics.py", "View results and trigger collection"),
        ("monitor_synergy_metrics.py", "Monitor collection progress"),
        ("simple_philips_test.py", "Simple access test"),
        ("philips_github_metrics_dag.py", "Main Airflow DAG")
    ]
    
    for script, description in scripts:
        if os.path.exists(script):
            print(f"   ✅ {script:<30} - {description}")
        else:
            print(f"   ❌ {script:<30} - {description} (MISSING)")
    
    print("\n🔧 Prerequisites Check:")
    print("   □ GitHub token with philips-internal access")
    print("   □ Member of philips-internal organization") 
    print("   □ Access to hmp-synergy-blr team")
    print("   □ Airflow running in WSL")
    print("   □ Python dependencies installed")
    
    print("\n💡 Quick Commands:")
    print("   # Test everything:")
    print("   python test_philips_access.py && python test_synergy_base.py")
    print()
    print("   # Start collection:")
    print("   python view_philips_metrics.py --trigger")
    print()
    print("   # Monitor and view:")
    print("   python monitor_synergy_metrics.py")

if __name__ == "__main__":
    show_philips_quick_start()
