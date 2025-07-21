"""
Configuration module for GitHub metrics collection.
"""

import os
from typing import List, Dict, Any
from pydantic import BaseSettings, validator


class Settings(BaseSettings):
    """Application settings with validation."""
    
    # GitHub Configuration
    github_token: str
    github_repositories: List[str] = []
    
    # Collection Settings
    metrics_collection_days: int = 30
    collection_timezone: str = "UTC"
    
    # Airflow Settings
    airflow_home: str = "/opt/airflow"
    dag_schedule_interval: str = "@daily"
    
    # Database Settings (for future use)
    database_url: str = "sqlite:///github_metrics.db"
    
    # Output Settings
    metrics_output_dir: str = "/tmp/github_metrics"
    enable_dashboard: bool = True
    dashboard_host: str = "127.0.0.1"
    dashboard_port: int = 8050
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        env_prefix = "METRICS_"
        case_sensitive = False
    
    @validator('github_repositories', pre=True)
    def parse_repositories(cls, v):
        if isinstance(v, str):
            # Parse comma-separated string
            return [repo.strip() for repo in v.split(',') if repo.strip()]
        return v
    
    @validator('github_token')
    def validate_github_token(cls, v):
        if not v or len(v) < 20:
            raise ValueError('GitHub token must be provided and valid')
        return v


# Global settings instance
settings = Settings()


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
