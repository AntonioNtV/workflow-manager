from typing import Callable, Generic, Type, Any, Dict
from pydantic import BaseModel
from workflow.models import InputType, OutputType, StepContext


class Step(Generic[InputType, OutputType]):
    """
    A Step is an individual unit of work with defined inputs and outputs.
    
    Attributes:
        id: The unique identifier of the step
        name: The name of the step
        description: A brief description of what the step does
        input_schema: The Pydantic model class for step inputs
        output_schema: The Pydantic model class for step outputs
        func: The function that implements the step logic
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        input_schema: Type[InputType],
        output_schema: Type[OutputType],
        func: Callable[[InputType], Any],
        step_id: str = None,
    ):
        self.name = name
        self.description = description
        self.input_schema = input_schema
        self.output_schema = output_schema
        self.func = func
        self.id = step_id or name.lower().replace(" ", "_")
    
    async def execute(
        self, 
        context: StepContext
    ) -> OutputType:
        """
        Execute the step with the given context.
        
        Args:
            context: The execution context containing input data and step results
            
        Returns:
            The output data from the step
        """
        input_data = context.input_data
        
        # Validate input data
        validated_input = (
            self.input_schema.model_validate(input_data) 
            if not isinstance(input_data, self.input_schema) 
            else input_data
        )
        
        # Execute the step function
        result = await self.func(validated_input)
        
        # Validate output data
        if not isinstance(result, self.output_schema):
            result = self.output_schema.model_validate(result)
            
        return result 