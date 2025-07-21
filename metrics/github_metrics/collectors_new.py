"""
GitHub data collector module for repository metrics.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from github import Github
from github.Repository import Repository
from github.PullRequest import PullRequest
from github.Issue import Issue
import pandas as pd

logger = logging.getLogger(__name__)


class GitHubCollector:
    """Collects data from GitHub repositories using PyGithub."""
    
    def __init__(self, token: str):
        """
        Initialize GitHub collector with authentication token.
        
        Args:
            token: GitHub personal access token
        """
        self.github = Github(token)
        self.token = token
        
    def get_repository(self, repo_name: str) -> Repository:
        """Get repository object by name."""
        try:
            return self.github.get_repo(repo_name)
        except Exception as e:
            logger.error(f"Failed to get repository {repo_name}: {e}")
            raise
    
    def collect_pull_requests(
        self, 
        repo_name: str, 
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        state: str = "all",
        user_filter: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Collect pull request data from repository.
        
        Args:
            repo_name: Repository name in format "owner/repo"
            since: Start date for data collection
            until: End date for data collection  
            state: PR state filter ("open", "closed", "all")
            user_filter: List of GitHub usernames to filter by (optional)
            
        Returns:
            List of pull request data dictionaries filtered by specified users
        """
        repo = self.get_repository(repo_name)
        
        if since is None:
            since = datetime.now() - timedelta(days=30)
        if until is None:
            until = datetime.now()
            
        prs = []
        
        try:
            for pr in repo.get_pulls(state=state, sort="updated", direction="desc"):
                # Filter by date range
                if pr.updated_at < since:
                    break
                if pr.updated_at > until:
                    continue
                
                # Filter by users if specified
                if user_filter:
                    pr_author = pr.user.login if pr.user else None
                    if pr_author not in user_filter:
                        continue
                    
                pr_data = self._extract_pr_data(pr)
                prs.append(pr_data)
                
            logger.info(f"Collected {len(prs)} pull requests from {repo_name}")
            if user_filter:
                logger.info(f"Filtered by users: {', '.join(user_filter)}")
            return prs
            
        except Exception as e:
            logger.error(f"Failed to collect pull requests: {e}")
            raise
    
    def _extract_pr_data(self, pr: PullRequest) -> Dict[str, Any]:
        """Extract relevant data from a pull request."""
        
        # Calculate cycle time
        cycle_time = None
        if pr.closed_at and pr.created_at:
            cycle_time = (pr.closed_at - pr.created_at).total_seconds() / 3600  # hours
        
        # Get review data
        reviews = list(pr.get_reviews())
        review_count = len(reviews)
        
        # Get first review time
        first_review_time = None
        if reviews:
            first_review = min(reviews, key=lambda r: r.created_at)
            if first_review.created_at and pr.created_at:
                first_review_time = (first_review.created_at - pr.created_at).total_seconds() / 3600
        
        return {
            'id': pr.id,
            'number': pr.number,
            'title': pr.title,
            'author': pr.user.login if pr.user else None,
            'created_at': pr.created_at,
            'updated_at': pr.updated_at,
            'closed_at': pr.closed_at,
            'merged_at': pr.merged_at,
            'state': pr.state,
            'merged': pr.merged,
            'additions': pr.additions,
            'deletions': pr.deletions,
            'changed_files': pr.changed_files,
            'cycle_time_hours': cycle_time,
            'review_count': review_count,
            'first_review_time_hours': first_review_time,
            'base_branch': pr.base.ref,
            'head_branch': pr.head.ref,
            'draft': pr.draft,
            'url': pr.html_url
        }
    
    def collect_commits(
        self, 
        repo_name: str, 
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        user_filter: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Collect commit data from repository.
        
        Args:
            repo_name: Repository name in format "owner/repo"
            since: Start date for data collection
            until: End date for data collection
            user_filter: List of GitHub usernames to filter by (optional)
            
        Returns:
            List of commit data dictionaries filtered by specified users
        """
        repo = self.get_repository(repo_name)
        
        if since is None:
            since = datetime.now() - timedelta(days=30)
        if until is None:
            until = datetime.now()
            
        commits = []
        
        try:
            for commit in repo.get_commits(since=since, until=until):
                # Filter by users if specified
                if user_filter:
                    commit_author = None
                    if commit.author:
                        commit_author = commit.author.login
                    elif commit.commit.author:
                        # Fallback to commit.author.email if no GitHub user
                        commit_author = commit.commit.author.email
                    
                    if commit_author not in user_filter:
                        continue
                
                commit_data = self._extract_commit_data(commit)
                commits.append(commit_data)
                
            logger.info(f"Collected {len(commits)} commits from {repo_name}")
            if user_filter:
                logger.info(f"Filtered by users: {', '.join(user_filter)}")
            return commits
            
        except Exception as e:
            logger.error(f"Failed to collect commits: {e}")
            raise
    
    def _extract_commit_data(self, commit) -> Dict[str, Any]:
        """Extract relevant data from a commit."""
        
        return {
            'sha': commit.sha,
            'message': commit.commit.message,
            'author': commit.author.login if commit.author else None,
            'author_email': commit.commit.author.email if commit.commit.author else None,
            'authored_date': commit.commit.author.date if commit.commit.author else None,
            'committer': commit.committer.login if commit.committer else None,
            'committed_date': commit.commit.committer.date if commit.commit.committer else None,
            'additions': commit.stats.additions if commit.stats else 0,
            'deletions': commit.stats.deletions if commit.stats else 0,
            'total_changes': commit.stats.total if commit.stats else 0,
            'files_changed': len(commit.files) if commit.files else 0,
            'url': commit.html_url
        }
    
    def collect_issues(
        self, 
        repo_name: str, 
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        state: str = "all",
        user_filter: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Collect issue data from repository.
        
        Args:
            repo_name: Repository name in format "owner/repo"
            since: Start date for data collection
            until: End date for data collection
            state: Issue state filter ("open", "closed", "all")
            user_filter: List of GitHub usernames to filter by (optional)
            
        Returns:
            List of issue data dictionaries filtered by specified users
        """
        repo = self.get_repository(repo_name)
        
        if since is None:
            since = datetime.now() - timedelta(days=30)
        if until is None:
            until = datetime.now()
            
        issues = []
        
        try:
            for issue in repo.get_issues(state=state, sort="updated", direction="desc"):
                # Skip pull requests (GitHub API includes PRs in issues)
                if issue.pull_request:
                    continue
                
                # Filter by date range
                if issue.updated_at < since:
                    break
                if issue.updated_at > until:
                    continue
                
                # Filter by users if specified
                if user_filter:
                    issue_author = issue.user.login if issue.user else None
                    if issue_author not in user_filter:
                        continue
                    
                issue_data = self._extract_issue_data(issue)
                issues.append(issue_data)
                
            logger.info(f"Collected {len(issues)} issues from {repo_name}")
            if user_filter:
                logger.info(f"Filtered by users: {', '.join(user_filter)}")
            return issues
            
        except Exception as e:
            logger.error(f"Failed to collect issues: {e}")
            raise
    
    def _extract_issue_data(self, issue: Issue) -> Dict[str, Any]:
        """Extract relevant data from an issue."""
        
        # Calculate resolution time
        resolution_time = None
        if issue.closed_at and issue.created_at:
            resolution_time = (issue.closed_at - issue.created_at).total_seconds() / 3600  # hours
        
        return {
            'id': issue.id,
            'number': issue.number,
            'title': issue.title,
            'author': issue.user.login if issue.user else None,
            'created_at': issue.created_at,
            'updated_at': issue.updated_at,
            'closed_at': issue.closed_at,
            'state': issue.state,
            'labels': [label.name for label in issue.labels],
            'assignees': [assignee.login for assignee in issue.assignees],
            'comments_count': issue.comments,
            'resolution_time_hours': resolution_time,
            'url': issue.html_url
        }
    
    def collect_deployments(
        self, 
        repo_name: str, 
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        user_filter: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Collect deployment data from repository.
        
        Args:
            repo_name: Repository name in format "owner/repo"
            since: Start date for data collection
            until: End date for data collection
            user_filter: List of GitHub usernames to filter by (optional)
            
        Returns:
            List of deployment data dictionaries filtered by specified users
        """
        repo = self.get_repository(repo_name)
        
        if since is None:
            since = datetime.now() - timedelta(days=30)
        if until is None:
            until = datetime.now()
            
        deployments = []
        
        try:
            for deployment in repo.get_deployments():
                # Filter by date range
                if deployment.created_at < since:
                    break
                if deployment.updated_at > until:
                    continue
                
                # Filter by users if specified (deployment creator)
                if user_filter:
                    deployment_creator = deployment.creator.login if deployment.creator else None
                    if deployment_creator not in user_filter:
                        continue
                
                deployment_data = self._extract_deployment_data(deployment)
                deployments.append(deployment_data)
                
            logger.info(f"Collected {len(deployments)} deployments from {repo_name}")
            if user_filter:
                logger.info(f"Filtered by users: {', '.join(user_filter)}")
            return deployments
            
        except Exception as e:
            logger.error(f"Failed to collect deployments: {e}")
            raise
    
    def _extract_deployment_data(self, deployment) -> Dict[str, Any]:
        """Extract relevant data from a deployment."""
        
        return {
            'id': deployment.id,
            'ref': deployment.ref,
            'sha': deployment.sha,
            'environment': deployment.environment,
            'creator': deployment.creator.login if deployment.creator else None,
            'created_at': deployment.created_at,
            'updated_at': deployment.updated_at,
            'description': deployment.description,
            'statuses_url': deployment.statuses_url,
            'url': deployment.url
        }
    
    def collect_all_data(
        self, 
        repo_name: str, 
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        user_filter: Optional[List[str]] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Collect all types of data from repository.
        
        Args:
            repo_name: Repository name in format "owner/repo"
            since: Start date for data collection
            until: End date for data collection
            user_filter: List of GitHub usernames to filter by (optional)
            
        Returns:
            Dictionary containing all collected data types filtered by specified users
        """
        logger.info(f"Collecting all data from {repo_name}")
        if user_filter:
            logger.info(f"Filtering by users: {', '.join(user_filter)}")
        
        return {
            'pull_requests': self.collect_pull_requests(repo_name, since, until, user_filter=user_filter),
            'commits': self.collect_commits(repo_name, since, until, user_filter=user_filter),
            'issues': self.collect_issues(repo_name, since, until, user_filter=user_filter),
            'deployments': self.collect_deployments(repo_name, since, until, user_filter=user_filter)
        }
