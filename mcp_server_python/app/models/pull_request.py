"""
PullRequest model definition
"""

import enum
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Index, String, Text
from sqlalchemy.orm import relationship

from app.models.base import Base


class PullRequestStatus(str, enum.Enum):
    """Pull request status enum"""
    DRAFT = "draft"
    OPEN = "open"
    MERGED = "merged"
    CLOSED = "closed"


class PullRequest(Base):
    """PullRequest model"""
    
    # Columns
    task_id = Column(
        String(36), 
        ForeignKey("task.id"), 
        nullable=False,
        index=True,
        comment="ID of the associated task"
    )
    repository_id = Column(
        String(36), 
        ForeignKey("repository.id"), 
        nullable=False,
        index=True,
        comment="ID of the associated repository"
    )
    pull_request_id = Column(String, nullable=True, index=True, comment="Pull request ID in Azure DevOps")
    title = Column(String, nullable=False, comment="Pull request title")
    description = Column(Text, nullable=True, comment="Pull request description")
    source_branch = Column(String, nullable=False, comment="Source branch name")
    target_branch = Column(String, nullable=False, default="main", comment="Target branch name")
    status = Column(
        Enum(PullRequestStatus),
        nullable=False,
        default=PullRequestStatus.DRAFT,
        index=True,
        comment="Current status of the pull request"
    )
    url = Column(String, nullable=True, comment="URL to the pull request")
    changed_files = Column(String, nullable=False, default="[]", comment="List of files changed in the PR")
    reviewers = Column(String, nullable=False, default="[]", comment="List of PR reviewers")
    created_in_azure_devops = Column(Boolean, nullable=False, default=False, comment="Whether the PR was created in Azure DevOps")
    created_in_azure_devops_at = Column(DateTime, nullable=True, comment="When the PR was created in Azure DevOps")
    merged_at = Column(DateTime, nullable=True, comment="When the PR was merged")
    closed_at = Column(DateTime, nullable=True, comment="When the PR was closed")
    metrics = Column(String, nullable=False, default="{}", comment="PR metrics (size, time to merge, etc.)")
    metadata = Column(String, nullable=False, default="{}", comment="Additional metadata for the PR")
    
    # Relationships
    task = relationship("Task", back_populates="pull_request")
    repository = relationship("Repository", back_populates="pull_requests")
    
    def dict(self) -> Dict[str, Any]:
        """Convert model to dictionary with nested relationships"""
        import json
        result = super().dict()
        
        # Parse JSON strings to dictionaries/lists
        try:
            result["changed_files"] = json.loads(result["changed_files"])
        except (TypeError, json.JSONDecodeError):
            result["changed_files"] = []
            
        try:
            result["reviewers"] = json.loads(result["reviewers"])
        except (TypeError, json.JSONDecodeError):
            result["reviewers"] = []
            
        try:
            result["metrics"] = json.loads(result["metrics"])
        except (TypeError, json.JSONDecodeError):
            result["metrics"] = {}
            
        try:
            result["metadata"] = json.loads(result["metadata"])
        except (TypeError, json.JSONDecodeError):
            result["metadata"] = {}
        
        # Add nested repository info
        if self.repository:
            result["repository"] = {
                "id": str(self.repository.id),
                "name": self.repository.name,
                "url": self.repository.url,
            }
            
        # Add task summary
        if self.task:
            result["task"] = {
                "id": str(self.task.id),
                "azure_devops_id": self.task.azure_devops_id,
                "title": self.task.title,
            }
            
        return result