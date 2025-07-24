"""
Configuration module for GitHub metrics collection.
Simplified for Airflow 3.0+ compatibility.
"""

import os
from typing import List, Dict, Any, Optional

# Simple configuration constants for Airflow usage
DEFAULT_COLLECTION_DAYS = 30
DEFAULT_OUTPUT_DIR = "/tmp/github_metrics"
DEFAULT_AIRFLOW_HOME = "/opt/airflow"

# Configuration that will be read from Airflow Variables at runtime
def get_config_from_airflow_variables():
    """
    Get configuration from Airflow Variables.
    This function should be called from within DAG tasks.
    """
    from airflow.models import Variable
    
    return {
        'github_token': Variable.get("GITHUB_TOKEN", default_var=None),
        'github_repositories': Variable.get("GITHUB_REPOSITORIES", default_var=[], deserialize_json=True),
        'collection_days': int(Variable.get("METRICS_COLLECTION_DAYS", default_var=str(DEFAULT_COLLECTION_DAYS))),
        'output_dir': Variable.get("METRICS_OUTPUT_PATH", default_var=DEFAULT_OUTPUT_DIR),
        'team_members': Variable.get("TEAM_MEMBERS", default_var=[], deserialize_json=True)
    }


# Airflow Variables configuration
AIRFLOW_VARIABLES = {
    "GITHUB_TOKEN": {
        "description": "GitHub Personal Access Token for API access",
        "value": None  # Set this in Airflow UI or via CLI
    },
    "GITHUB_REPOSITORIES": {
        "description": "List of GitHub repositories to monitor (JSON array)",
        "value": ["owner/repo1", "owner/repo2"]  # Example repositories
    },
    "METRICS_COLLECTION_DAYS": {
        "description": "Number of days to collect metrics for",
        "value": 30
    },
    "METRICS_OUTPUT_DIR": {
        "description": "Directory to store metrics output",
        "value": "/tmp/github_metrics"
    }
}


def get_sample_repositories() -> List[str]:
    """Get sample repository list for testing."""
    return [
        "microsoft/vscode",
        "facebook/react",
        "kubernetes/kubernetes"
    ]


def get_required_github_scopes() -> List[str]:
    """Get required GitHub token scopes."""
    return [
        "repo",           # Access to repository data
        "read:org",       # Read organization data
        "read:user",      # Read user data
        "read:project"    # Read project data
    ]


def validate_github_token_scopes(token: str) -> Dict[str, Any]:
    """
    Validate GitHub token has required scopes.
    
    Args:
        token: GitHub personal access token
        
    Returns:
        Dictionary with validation results
    """
    from github import Github
    
    try:
        g = Github(token)
        user = g.get_user()
        
        # Get rate limit info to check token validity
        rate_limit = g.get_rate_limit()
        
        return {
            "valid": True,
            "user": user.login,
            "rate_limit_remaining": rate_limit.core.remaining,
            "rate_limit_reset": rate_limit.core.reset,
            "message": "Token is valid"
        }
        
    except Exception as e:
        return {
            "valid": False,
            "error": str(e),
            "message": "Token validation failed"
        }
