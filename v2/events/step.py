from enum import Enum
from pydantic import BaseModel
from uuid import UUID
from typing import Any


class StepEventType(Enum):
    """Types of events that can be emitted during step execution."""
    STEP_STARTED = "step_started"
    STEP_COMPLETED = "step_completed"
    STEP_FAILED = "step_failed"

class StepEvent(BaseModel):
    """Base class for all step events."""
    type: StepEventType
    step_id: UUID
    step_name: str

class StepStartedEvent(StepEvent):
    """Event emitted when a step starts execution."""
    type: StepEventType = StepEventType.STEP_STARTED
    input_data: Any = None

class StepCompletedEvent(StepEvent):
    """Event emitted when a step completes execution."""
    type: StepEventType = StepEventType.STEP_COMPLETED
    input_data: Any = None
    output_data: Any = None

class StepFailedEvent(StepEvent):
    """Event emitted when a step fails execution."""
    type: StepEventType = StepEventType.STEP_FAILED
    input_data: BaseModel = None
    error: str = None