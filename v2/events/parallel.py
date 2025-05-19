from typing import Any, Dict
from pydantic import BaseModel
from enum import Enum

class ParallelEventType(str, Enum):
    PARALLEL_STARTED = "parallel_started"
    PARALLEL_COMPLETED = "parallel_completed"

class ParallelEvent(BaseModel):
    type: ParallelEventType
    output_data: Dict[str, Any]
    
    