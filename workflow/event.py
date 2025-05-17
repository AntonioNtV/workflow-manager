from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field

class EventType(Enum):
    """Types of events that can be emitted during workflow execution."""
    STEP_STARTED = "step_started"
    STEP_COMPLETED = "step_completed"
    WORKFLOW_STARTED = "workflow_started"
    WORKFLOW_COMPLETED = "workflow_completed"
    WORKFLOW_FAILED = "workflow_failed"

class Event(BaseModel):
    """Base class for all workflow events."""
    type: EventType
    workflow_name: str
    timestamp: float = Field(default_factory=lambda: __import__('time').time())

# Step events
class StepEvent(Event):
    """Base class for events related to step execution."""
    step_id: str
    step_name: str

class StepStartedEvent(StepEvent):
    """Event emitted when a step starts execution."""
    type: EventType = EventType.STEP_STARTED
    input_data: Any = None

class StepCompletedEvent(StepEvent):
    """Event emitted when a step completes execution."""
    type: EventType = EventType.STEP_COMPLETED
    output_data: Any = None
    execution_time: float = 0.0

# Workflow events
class WorkflowEvent(Event):
    """Base class for events related to workflow execution."""
    pass

class WorkflowStartedEvent(WorkflowEvent):
    """Event emitted when a workflow starts execution."""
    type: EventType = EventType.WORKFLOW_STARTED
    input_data: Any = None

class WorkflowCompletedEvent(WorkflowEvent):
    """Event emitted when a workflow completes execution."""
    type: EventType = EventType.WORKFLOW_COMPLETED
    output_data: Any = None
    execution_time: float = 0.0

class WorkflowFailedEvent(WorkflowEvent):
    """Event emitted when a workflow fails execution."""
    type: EventType = EventType.WORKFLOW_FAILED
    error: str
    execution_time: float = 0.0 