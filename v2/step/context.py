from pydantic import BaseModel
from typing import Any, Dict, Union

class StepContext(BaseModel):
    """
    Context object passed to steps during execution.
    
    Provides access to:
    - The input data for the current step
    - Results from previously executed steps
    - The initial input data for the workflow
    """
    input_data: Any