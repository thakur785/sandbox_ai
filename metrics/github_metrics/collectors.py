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
            
        # Get review comments count
        review_comments = pr.review_comments
        issue_comments = pr.comments
        
        # Get commit data
        commits = list(pr.get_commits())
        
        return {
            "id": pr.id,
            "number": pr.number,
            "title": pr.title,
            "state": pr.state,
            "created_at": pr.created_at,
            "updated_at": pr.updated_at,
            "closed_at": pr.closed_at,
            "merged_at": pr.merged_at,
            "merged": pr.merged,
            "author": pr.user.login if pr.user else None,
            "assignees": [a.login for a in pr.assignees],
            "reviewers": [r.login for r in pr.requested_reviewers],
            "labels": [l.name for l in pr.labels],
            "additions": pr.additions,
            "deletions": pr.deletions,
            "changed_files": pr.changed_files,
            "commits_count": len(commits),
            "review_comments": review_comments,
            "issue_comments": issue_comments,
            "total_comments": review_comments + issue_comments,
            "cycle_time_hours": cycle_time,
            "url": pr.html_url
        }
    
    def collect_commits(
        self, 
        repo_name: str, 
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        author: Optional[str] = None,
        user_filter: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Collect commit data from repository.
        
        Args:
            repo_name: Repository name in format "owner/repo"
            since: Start date for data collection
            until: End date for data collection
            author: Filter commits by author email (optional)
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
            kwargs = {"since": since, "until": until}
            if author:
                kwargs["author"] = author
                
            for commit in repo.get_commits(**kwargs):
                # Filter by users if specified
                if user_filter:
                    commit_author = commit.author.login if commit.author else None
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
            "sha": commit.sha,
            "message": commit.commit.message,
            "author_name": commit.commit.author.name if commit.commit.author else None,
            "author_email": commit.commit.author.email if commit.commit.author else None,
            "author_login": commit.author.login if commit.author else None,
            "committer_name": commit.commit.committer.name if commit.commit.committer else None,
            "committer_email": commit.commit.committer.email if commit.commit.committer else None,
            "authored_date": commit.commit.author.date if commit.commit.author else None,
            "committed_date": commit.commit.committer.date if commit.commit.committer else None,
            "additions": commit.stats.additions,
            "deletions": commit.stats.deletions,
            "total_changes": commit.stats.total,
            "files_changed": len(commit.files),
            "url": commit.html_url
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
                # Skip pull requests (they show up as issues in GitHub API)
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
            "id": issue.id,
            "number": issue.number,
            "title": issue.title,
            "body": issue.body,
            "state": issue.state,
            "created_at": issue.created_at,
            "updated_at": issue.updated_at,
            "closed_at": issue.closed_at,
            "author": issue.user.login if issue.user else None,
            "assignees": [a.login for a in issue.assignees],
            "labels": [l.name for l in issue.labels],
            "comments": issue.comments,
            "resolution_time_hours": resolution_time,
            "url": issue.html_url
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
            List of deployment data dictionaries
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
                if deployment.created_at > until:
                    continue
                
                # Filter by users if specified
                if user_filter:
                    creator = deployment.creator.login if deployment.creator else None
                    if creator not in user_filter:
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
            "id": deployment.id,
            "sha": deployment.sha,
            "ref": deployment.ref,
            "environment": deployment.environment,
            "description": deployment.description,
            "created_at": deployment.created_at,
            "updated_at": deployment.updated_at,
            "creator": deployment.creator.login if deployment.creator else None,
            "statuses_url": deployment.statuses_url,
            "url": deployment.url
        }
    
    def collect_all_data(
        self, 
        repo_name: str, 
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        user_filter: Optional[List[str]] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Collect all data types from repository.
        
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
