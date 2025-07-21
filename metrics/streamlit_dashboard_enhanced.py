#!/usr/bin/env python3
"""
Enhanced GitHub Metrics Dashboard with Hardcoded Configuration
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from datetime import datetime, timedelta
import os

# Import our GitHub metrics modules
try:
    from github_metrics.collectors import GitHubCollector
    from github_metrics.metrics import DORAMetrics, PRMetrics, ProductivityMetrics
    MODULES_AVAILABLE = True
except ImportError:
    MODULES_AVAILABLE = False

# 🔧 HARDCODED CONFIGURATION
# =========================

# Default repositories (easily customizable)
DEFAULT_REPOSITORIES = [
    "microsoft/vscode",
    "facebook/react", 
    "vercel/next.js",
    "google/go",
    "python/cpython",
]

# Team configurations
TEAM_CONFIGURATIONS = {
    "Frontend Team": {
        "repos": ["facebook/react", "vercel/next.js"],
        "users": ["gaearon", "sebmarkbage", "acdlite", "timneutkens", "ijjk"]
    },
    "Platform Team": {
        "repos": ["microsoft/vscode", "google/go"],
        "users": ["jrieken", "alexdima", "bpasero", "rsc", "bradfitz"]
    },
    "Full Stack Team": {
        "repos": ["python/cpython", "vercel/next.js"],
        "users": ["gvanrossum", "timneutkens", "ijjk", "styfle"]
    },
    "Custom Team": {
        "repos": ["your-org/repo1", "your-org/repo2"],
        "users": ["john.doe", "jane.smith", "dev.lead"]
    }
}

# Dashboard settings
DEFAULT_DAYS = 30
DEFAULT_TEAM = "Frontend Team"


class GitHubMetricsDashboard:
    def __init__(self):
        self.github_token = None
        self.collector = None
        self.setup_page_config()
        
    def setup_page_config(self):
        """Configure Streamlit page."""
        st.set_page_config(
            page_title="GitHub Metrics Dashboard",
            page_icon="📊",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
    def load_sample_data(self):
        """Load sample data if no real data is available."""
        try:
            with open('sample_metrics.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Return default sample data
            return {
                "dora_metrics": {
                    "deployment_frequency": {"deployments_per_week": 3.5},
                    "lead_time_for_changes": {"median_lead_time_hours": 22.0},
                    "mean_time_to_recovery": {"median_recovery_time_hours": 4.5},
                    "change_failure_rate": {"change_failure_rate": 0.08}
                },
                "pr_metrics": {
                    "cycle_time_analysis": {"mean_cycle_time_hours": 32.4},
                    "review_analysis": {"mean_review_comments": 4.2},
                    "merge_analysis": {"merge_rate": 0.76, "total_prs": 125}
                },
                "productivity_metrics": {
                    "developer_activity": {
                        "commit_activity": {"total_authors": 12, "total_commits": 380}
                    },
                    "collaboration_metrics": {"collaboration_pairs": 45}
                }
            }
    
    def render_sidebar(self):
        """Render sidebar configuration."""
        st.sidebar.header("🔧 Configuration")
        
        # Team selection
        selected_team = st.sidebar.selectbox(
            "Select Team Configuration",
            options=list(TEAM_CONFIGURATIONS.keys()),
            index=list(TEAM_CONFIGURATIONS.keys()).index(DEFAULT_TEAM)
        )
        
        team_config = TEAM_CONFIGURATIONS[selected_team]
        
        # Show team details
        st.sidebar.subheader(f"👥 {selected_team}")
        st.sidebar.write("**Repositories:**")
        for repo in team_config["repos"]:
            st.sidebar.write(f"• {repo}")
            
        st.sidebar.write("**Team Members:**")
        for user in team_config["users"]:
            st.sidebar.write(f"• {user}")
        
        # Date range
        days_back = st.sidebar.slider(
            "📅 Days to Analyze",
            min_value=7,
            max_value=90,
            value=DEFAULT_DAYS,
            step=7
        )
        
        # GitHub token
        st.sidebar.subheader("🔑 Authentication")
        token_input = st.sidebar.text_input(
            "GitHub Token (Optional)",
            type="password",
            help="Paste your GitHub Personal Access Token for higher rate limits"
        )
        
        # Use sample data toggle
        use_sample = st.sidebar.checkbox(
            "📋 Use Sample Data",
            value=True,
            help="Use pre-generated sample data instead of live GitHub API"
        )
        
        return selected_team, team_config, days_back, token_input, use_sample
    
    def collect_metrics(self, team_config, days_back, token):
        """Collect metrics from GitHub API."""
        if not MODULES_AVAILABLE:
            st.error("GitHub metrics modules not available. Using sample data.")
            return self.load_sample_data()
            
        try:
            collector = GitHubCollector(token)
            since_date = datetime.now() - timedelta(days=days_back)
            
            all_metrics = {
                "dora_metrics": {},
                "pr_metrics": {},
                "productivity_metrics": {}
            }
            
            # Collect from all team repositories
            for repo in team_config["repos"]:
                try:
                    data = collector.collect_all_data(
                        repo_name=repo,
                        since=since_date,
                        user_filter=team_config["users"]
                    )
                    
                    # Calculate metrics
                    dora_calc = DORAMetrics(data)
                    pr_calc = PRMetrics(data)
                    prod_calc = ProductivityMetrics(data)
                    
                    # Aggregate metrics (simplified)
                    if not all_metrics["dora_metrics"]:
                        all_metrics["dora_metrics"] = dora_calc.get_all_dora_metrics(days_back)
                        all_metrics["pr_metrics"] = pr_calc.get_all_pr_metrics()
                        all_metrics["productivity_metrics"] = prod_calc.get_all_productivity_metrics()
                    
                except Exception as e:
                    st.warning(f"Failed to collect data from {repo}: {e}")
                    
            return all_metrics
            
        except Exception as e:
            st.error(f"Failed to collect metrics: {e}")
            return self.load_sample_data()
    
    def render_dora_metrics(self, metrics):
        """Render DORA metrics section."""
        st.header("🎯 DORA Metrics")
        
        dora = metrics.get("dora_metrics", {})
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            deployment_freq = dora.get("deployment_frequency", {}).get("deployments_per_week", 0)
            st.metric(
                "📈 Deployment Frequency",
                f"{deployment_freq:.1f}/week",
                delta="↗️ Good" if deployment_freq > 1 else "⚠️ Low"
            )
            
        with col2:
            lead_time = dora.get("lead_time_for_changes", {}).get("median_lead_time_hours", 0)
            st.metric(
                "⏱️ Lead Time",
                f"{lead_time:.1f}h",
                delta="✅ Fast" if lead_time < 24 else "⚠️ Slow"
            )
            
        with col3:
            mttr = dora.get("mean_time_to_recovery", {}).get("median_recovery_time_hours", 0)
            st.metric(
                "🔧 MTTR",
                f"{mttr:.1f}h",
                delta="✅ Good" if mttr < 8 else "⚠️ High"
            )
            
        with col4:
            cfr = dora.get("change_failure_rate", {}).get("change_failure_rate", 0)
            st.metric(
                "💥 Change Failure Rate",
                f"{cfr:.1%}",
                delta="✅ Low" if cfr < 0.15 else "⚠️ High"
            )
    
    def render_pr_metrics(self, metrics):
        """Render PR metrics section."""
        st.header("📋 Pull Request Metrics")
        
        pr_metrics = metrics.get("pr_metrics", {})
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("⏰ Cycle Time Analysis")
            cycle_data = pr_metrics.get("cycle_time_analysis", {})
            
            cycle_metrics = {
                "Mean": cycle_data.get("mean_cycle_time_hours", 0),
                "Median": cycle_data.get("median_cycle_time_hours", 0),
                "P75": cycle_data.get("p75_cycle_time_hours", 0),
                "P95": cycle_data.get("p95_cycle_time_hours", 0)
            }
            
            fig = px.bar(
                x=list(cycle_metrics.keys()),
                y=list(cycle_metrics.values()),
                title="Cycle Time Distribution (Hours)",
                color=list(cycle_metrics.values()),
                color_continuous_scale="Viridis"
            )
            st.plotly_chart(fig, use_container_width=True)
            
        with col2:
            st.subheader("📊 Merge Analysis")
            merge_data = pr_metrics.get("merge_analysis", {})
            
            merge_rate = merge_data.get("merge_rate", 0)
            total_prs = merge_data.get("total_prs", 0)
            
            st.metric("✅ Merge Rate", f"{merge_rate:.1%}")
            st.metric("📋 Total PRs", total_prs)
            
            # Pie chart for PR status distribution
            merged = int(total_prs * merge_rate)
            closed = merge_data.get("closed_unmerged_prs", 0)
            open_prs = merge_data.get("open_prs", 0)
            
            fig = px.pie(
                values=[merged, closed, open_prs],
                names=["Merged", "Closed", "Open"],
                title="PR Status Distribution",
                color_discrete_sequence=["#00cc88", "#ff6b6b", "#ffd93d"]
            )
            st.plotly_chart(fig, use_container_width=True)
    
    def render_productivity_metrics(self, metrics):
        """Render productivity metrics section."""
        st.header("🏆 Productivity Metrics")
        
        prod_metrics = metrics.get("productivity_metrics", {})
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            dev_activity = prod_metrics.get("developer_activity", {})
            commit_activity = dev_activity.get("commit_activity", {})
            
            st.metric("👨‍💻 Active Developers", commit_activity.get("total_authors", 0))
            st.metric("📝 Total Commits", commit_activity.get("total_commits", 0))
            st.metric("📊 Avg Commits/Dev", f"{commit_activity.get('mean_commits_per_author', 0):.1f}")
            
        with col2:
            collaboration = prod_metrics.get("collaboration_metrics", {})
            
            st.metric("🤝 Collaboration Pairs", collaboration.get("collaboration_pairs", 0))
            st.metric("👥 Total Reviewers", collaboration.get("total_reviewers", 0))
            st.metric("📝 Avg Reviewers/PR", f"{collaboration.get('avg_reviewers_per_pr', 0):.1f}")
            
        with col3:
            pr_activity = dev_activity.get("pr_activity", {})
            
            st.metric("📋 Total PRs", pr_activity.get("total_prs", 0))
            st.metric("👨‍💻 PR Authors", pr_activity.get("pr_authors", 0))
            st.metric("📊 Avg PRs/Author", f"{pr_activity.get('mean_prs_per_author', 0):.1f}")
    
    def render_configuration_guide(self):
        """Render configuration guide."""
        with st.expander("🔧 Customization Guide"):
            st.markdown("""
            ### How to Customize This Dashboard
            
            **1. Edit Team Configurations:**
            ```python
            TEAM_CONFIGURATIONS = {
                "Your Team": {
                    "repos": ["your-org/repo1", "your-org/repo2"],
                    "users": ["john.doe", "jane.smith", "dev.lead"]
                }
            }
            ```
            
            **2. Add Your Repositories:**
            ```python
            DEFAULT_REPOSITORIES = [
                "your-org/backend-api",
                "your-org/frontend-app",
                "your-org/mobile-app"
            ]
            ```
            
            **3. GitHub Token Setup:**
            - Go to: https://github.com/settings/tokens
            - Generate new token with 'repo' scope
            - Paste token in sidebar
            
            **4. Environment Variables:**
            ```bash
            export GITHUB_TOKEN="your_token_here"
            ```
            """)
    
    def run(self):
        """Main dashboard application."""
        st.title("📊 GitHub Metrics Dashboard")
        st.markdown("**Team-focused metrics with hardcoded configuration**")
        
        # Sidebar configuration
        selected_team, team_config, days_back, token, use_sample = self.render_sidebar()
        
        # Main content
        if use_sample:
            st.info("🔍 Using sample data for demonstration")
            metrics = self.load_sample_data()
        else:
            if not token:
                st.warning("⚠️ No GitHub token provided. Using limited unauthenticated access.")
                token = None
            
            with st.spinner(f"📊 Collecting metrics for {selected_team}..."):
                metrics = self.collect_metrics(team_config, days_back, token)
        
        # Render metrics sections
        self.render_dora_metrics(metrics)
        st.divider()
        
        self.render_pr_metrics(metrics)
        st.divider()
        
        self.render_productivity_metrics(metrics)
        st.divider()
        
        # Configuration guide
        self.render_configuration_guide()
        
        # Footer
        st.markdown("---")
        st.markdown(f"**Current Configuration:** {selected_team} | **Analysis Period:** {days_back} days")


if __name__ == "__main__":
    dashboard = GitHubMetricsDashboard()
    dashboard.run()
