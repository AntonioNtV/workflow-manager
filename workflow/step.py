from typing import Callable, Generic, Type, TypeVar
from pydantic import BaseModel

from workflow.context import StepContext

InputType = TypeVar("InputType", bound=BaseModel)
OutputType = TypeVar("OutputType", bound=BaseModel)

class Step(Generic[InputType, OutputType]):
    """
    A Step is an individual unit of work with defined inputs and outputs.
    
    Attributes:
        name: The name of the step
        description: A brief description of what the step does
        input_schema: The Pydantic model class for step inputs
        output_schema: The Pydantic model class for step outputs
        resume_schema: Optional Pydantic model class for resuming interrupted steps
        func: The function that implements the step logic
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        input_schema: Type[InputType],
        output_schema: Type[OutputType],
        func: Callable[[InputType], OutputType],
    ):
        self.name = name
        self.description = description
        self.input_schema = input_schema
        self.output_schema = output_schema
        self.func = func
        self.id = name.lower().replace(" ", "_")
    
    async def execute(
        self, 
        context: StepContext
    ) -> OutputType:
        """
        Execute the step with the given input data or context.
        
        Args:
            context_or_input: Either a StepContext object or the input data for the step
            resume_data: Optional data for resuming an interrupted step
            
        Returns:
            The output data from the step
        """
        # Check if we're receiving a StepContext or raw input data

        input_data = context.input_data
        
        # Validate input data
        validated_input = (
            self.input_schema.model_validate(input_data) 
            if not isinstance(input_data, self.input_schema) 
            else input_data
        )
        
        result = await self.func(validated_input)
        
        # Validate output data
        if not isinstance(result, self.output_schema):
            result = self.output_schema.model_validate(result)
            
        return result 