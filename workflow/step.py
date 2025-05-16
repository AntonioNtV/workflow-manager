from typing import Any, Callable, Generic, Optional, Type, TypeVar, Dict, Union
from pydantic import BaseModel

InputType = TypeVar("InputType", bound=BaseModel)
OutputType = TypeVar("OutputType", bound=BaseModel)
ResumeType = TypeVar("ResumeType", bound=BaseModel)


# Forward references for type hints
class StepContext: pass


class Step(Generic[InputType, OutputType, ResumeType]):
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
        func: Callable[[Union[InputType, "StepContext"], Optional[ResumeType]], OutputType],
        resume_schema: Optional[Type[ResumeType]] = None,
    ):
        self.name = name
        self.description = description
        self.input_schema = input_schema
        self.output_schema = output_schema
        self.resume_schema = resume_schema
        self.func = func
        self.id = name.lower().replace(" ", "_")
    
    async def execute(
        self, 
        context_or_input: Any, 
        resume_data: Optional[Any] = None
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
        from workflow.workflow import StepContext
        
        if isinstance(context_or_input, StepContext):
            # We're being called with a StepContext
            context = context_or_input
            input_data = context.input_data
        else:
            # We're being called with raw input data
            # This is for backward compatibility
            input_data = context_or_input
            context = None
        
        # Validate input data
        validated_input = (
            self.input_schema.model_validate(input_data) 
            if not isinstance(input_data, self.input_schema) 
            else input_data
        )
        
        # Update context if we have one
        if context:
            context.input_data = validated_input
            context_or_input = context
        else:
            context_or_input = validated_input
        
        # Validate resume data if provided
        validated_resume = None
        if resume_data and self.resume_schema:
            validated_resume = (
                self.resume_schema.model_validate(resume_data)
                if not isinstance(resume_data, self.resume_schema)
                else resume_data
            )
        
        # Execute the step function
        # Pass validated_input instead of context_or_input when we have a context
        if isinstance(context_or_input, StepContext):
            result = await self.func(validated_input, validated_resume)
        else:
            result = await self.func(context_or_input, validated_resume)
        
        # Validate output data
        if not isinstance(result, self.output_schema):
            result = self.output_schema.model_validate(result)
            
        return result 