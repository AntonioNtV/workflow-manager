from typing import Any, Optional
from workflow.models import Event, EventType


class WorkflowEvent(Event):
    """Base class for workflow execution events."""
    workflow_name: str
    output_data: Optional[Any] = None


class StepEvent(WorkflowEvent):
    """Event for step execution updates."""
    step_id: str
    step_name: str


class StepStartedEvent(StepEvent):
    """Event emitted when a step starts executing."""
    type: EventType = EventType.STEP_STARTED
    input_data: Any


class StepCompletedEvent(StepEvent):
    """Event emitted when a step completes execution."""
    type: EventType = EventType.STEP_COMPLETED
    output_data: Any
    execution_time: float


class StepFailedEvent(StepEvent):
    """Event emitted when a step fails execution."""
    type: EventType = EventType.STEP_FAILED
    error: str
    execution_time: float


class WorkflowStartedEvent(WorkflowEvent):
    """Event emitted when the workflow starts executing."""
    type: EventType = EventType.WORKFLOW_STARTED
    input_data: Any


class WorkflowCompletedEvent(WorkflowEvent):
    """Event emitted when the workflow completes execution."""
    type: EventType = EventType.WORKFLOW_COMPLETED
    output_data: Any
    execution_time: float


class WorkflowFailedEvent(WorkflowEvent):
    """Event emitted when the workflow fails execution."""
    type: EventType = EventType.WORKFLOW_FAILED
    error: str
    execution_time: float 