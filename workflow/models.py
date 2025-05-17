from typing import Dict, Any
from pydantic import BaseModel

class StepContext(BaseModel):
    """
    Context object passed to steps during execution.
    
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

# Example models used in examples - these would typically be defined by the user
class UserInput(BaseModel):
    """User input model for workflow examples."""
    name: str
    age: int

class GreetingOutput(BaseModel):
    """Greeting output model for workflow examples."""
    message: str

class ProcessedOutput(BaseModel):
    """Processed output model for workflow examples."""
    original_message: str
    processed_data: list[str] 