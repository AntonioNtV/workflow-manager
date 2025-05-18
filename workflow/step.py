import inspect
from typing import Any, Callable, Type, Optional

from pydantic import BaseModel

class Step:
    """
    Represents a single step in a workflow.
    
    A step contains:
    - A function to execute
    - Input and output schemas for validation
    - Metadata like name and description
    """
    
    def __init__(
        self,
        name: str,
        func: Callable,
        input_schema: Type[BaseModel],
        id: str,
        output_schema: Optional[Type] = None,
        description: str = "",
    ):
        """
        Initialize a step.
        
        Args:
            name: The name of the step
            func: The async function to execute for this step
            input_schema: The Pydantic model for validating the input
            id: ID for the step
            output_schema: The Pydantic model for validating the output, optional
            description: A description of what the step does
        """
        self.name = name
        self.func = func
        self.input_schema = input_schema
        self.output_schema = output_schema
        self.description = description
        self.id = id
        
        # Validate function signature
        self._validate_func()
    
    def _validate_func(self) -> None:
        """Validate that the function has the correct signature."""
        if not inspect.iscoroutinefunction(self.func):
            raise ValueError(f"Step function '{self.name}' must be an async function")
        
        params = inspect.signature(self.func).parameters
        if len(params) != 1:
            raise ValueError(f"Step function '{self.name}' must accept exactly one parameter")
    
    async def execute(self, input_data: Any) -> Any:
        """
        Execute the step function with the given input data.
        
        Args:
            input_data: The input data for the step
            
        Returns:
            The output data from the step
        """
        # Validate input data if it's not already an instance of input_schema
        validated_input = (
            self.input_schema.model_validate(input_data)
            if not isinstance(input_data, self.input_schema)
            else input_data
        )
        
        # Execute the step function
        result = await self.func(validated_input)
        
        # Validate output if output_schema is provided
        if self.output_schema is not None and not isinstance(result, self.output_schema):
            # Only attempt validation for non-primitive types
            if isinstance(result, (dict, list)) or hasattr(result, "__dict__"):
                result = self.output_schema.model_validate(result)
        
        return result 