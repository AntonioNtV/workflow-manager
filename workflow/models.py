from typing import TypeVar, Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel

# Common type variables
InputType = TypeVar("InputType", bound=BaseModel)
OutputType = TypeVar("OutputType", bound=BaseModel)

# Event related models
class EventType(Enum):
    STEP_STARTED = "step_started"
    STEP_COMPLETED = "step_completed"
    WORKFLOW_STARTED = "workflow_started"
    WORKFLOW_COMPLETED = "workflow_completed"
    WORKFLOW_FAILED = "workflow_failed"
    STEP_FAILED = "step_failed"

class Event(BaseModel):
    """Base class for all system events."""
    type: EventType

# Context related models
class StepContext(BaseModel):
    """
    Context object passed to each step during execution.
    
    Provides access to:
    - The input data for the current step
    - Results from previously executed steps
    - The initial input data for the workflow
    """
    input_data: Any
    step_results: Dict[str, Any] = {}
    initial_data: Any = None
    workflow_name: str = ""
    
    def get_step_result(self, step_id: str) -> Any:
        """Get the result of a previously executed step by ID."""
        if step_id not in self.step_results:
            raise KeyError(f"No result found for step with ID: {step_id}")
        return self.step_results[step_id]
    
    def get_initial_data(self) -> Any:
        """Get the initial input data provided to the workflow."""
        return self.initial_data 