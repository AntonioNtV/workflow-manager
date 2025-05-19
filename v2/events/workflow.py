from enum import Enum
from typing import Any
from pydantic import BaseModel


class WorkflowEventType(Enum):
    """Types of events that can be emitted during workflow execution."""
    WORKFLOW_STARTED = "workflow_started"
    WORKFLOW_COMPLETED = "workflow_completed"
    WORKFLOW_FAILED = "workflow_failed"

class WorkflowEvent(BaseModel):
    """Base class for all workflow events."""
    type: WorkflowEventType
    workflow_id: str
    workflow_name: str

class WorkflowStartedEvent(WorkflowEvent):
    """Event emitted when a workflow starts execution."""
    type: WorkflowEventType = WorkflowEventType.WORKFLOW_STARTED

class WorkflowCompletedEvent(WorkflowEvent):
    """Event emitted when a workflow completes execution."""
    type: WorkflowEventType = WorkflowEventType.WORKFLOW_COMPLETED

class WorkflowFailedEvent(WorkflowEvent):
    """Event emitted when a workflow fails execution."""
    type: WorkflowEventType = WorkflowEventType.WORKFLOW_FAILED
    error: str = None