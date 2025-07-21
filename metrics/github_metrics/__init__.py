"""
GitHub Metrics Tracking System

A comprehensive system for tracking GitHub repository metrics including:
- PR cycle time
- Code review comments
- Productivity improvements  
- DORA metrics (Deployment frequency, Lead time, Mean time to recovery, Change failure rate)

This package uses Apache Airflow for orchestration and PyGithub for data collection.
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .collectors import GitHubCollector
from .metrics import DORAMetrics, ProductivityMetrics, PRMetrics
from .dashboard import MetricsDashboard

__all__ = [
    "GitHubCollector",
    "DORAMetrics", 
    "ProductivityMetrics",
    "PRMetrics",
    "MetricsDashboard"
]
