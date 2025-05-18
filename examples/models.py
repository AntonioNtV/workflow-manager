from pydantic import BaseModel

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