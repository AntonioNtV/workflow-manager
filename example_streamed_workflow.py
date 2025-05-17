import asyncio
from typing import List
from pydantic import BaseModel

from workflow import (
    Step, Workflow, SystemRunner, StepContext,
    Event, WorkflowStartedEvent, WorkflowCompletedEvent,
    StepStartedEvent, StepCompletedEvent
)

# Define input and output models
class UserInput(BaseModel):
    name: str
    age: int

class GreetingOutput(BaseModel):
    message: str

class ProcessedOutput(BaseModel):
    original_message: str
    processed_data: List[str]

# Define step functions
async def create_greeting(input_data: UserInput) -> GreetingOutput:
    """Generate a personalized greeting."""
    # Simulate some processing time
    await asyncio.sleep(1)
    message = f"Hello {input_data.name}, you are {input_data.age} years old!"
    return GreetingOutput(message=message)

async def process_data(input_data: GreetingOutput) -> ProcessedOutput:
    """Process the greeting into a structured format."""
    # Simulate some processing time
    await asyncio.sleep(1)
    # Split the message into words
    words = input_data.message.split()
    return ProcessedOutput(
        original_message=input_data.message,
        processed_data=words
    )

# Create workflow steps
greeting_step = Step(
    name="Create Greeting",
    description="Creates a personalized greeting message",
    input_schema=UserInput,
    output_schema=GreetingOutput,
    func=create_greeting
)

process_step = Step(
    name="Process Data",
    description="Processes the greeting into structured data",
    input_schema=GreetingOutput,
    output_schema=ProcessedOutput,
    func=process_data
)

# Create the workflow
workflow = Workflow(
    name="Greeting Workflow",
    description="A simple workflow that creates and processes a greeting",
    input_schema=UserInput
)

# Add steps to the workflow
workflow.then(greeting_step).then(process_step)

# Run the workflow with event streaming
async def main():
    # Create a runner
    runner = SystemRunner(workflow)
    
    # Input data
    user_data = UserInput(name="Alice", age=30)
    
    # Run the workflow with event streaming
    print("Starting workflow execution with event streaming...")
    
    result = None
    async for event in runner.run_streamed(user_data):
        # Handle different event types
        if isinstance(event, WorkflowStartedEvent):
            print(f"Workflow '{event.workflow_name}' started")
            print(f"Input data: {event.input_data}")
            
        elif isinstance(event, StepStartedEvent):
            print(f"Step '{event.step_name}' started")
            
        elif isinstance(event, StepCompletedEvent):
            print(f"Step '{event.step_name}' completed in {event.execution_time:.2f}s")
            print(f"Step output: {event.output_data}")
            
        elif isinstance(event, WorkflowCompletedEvent):
            print(f"Workflow '{event.workflow_name}' completed in {event.execution_time:.2f}s")
            print(f"Final output: {event.output_data}")
            result = event.output_data
    
    # Print final summary
    if result:
        print("\nWorkflow execution summary:")
        print(f"Original message: {result.original_message}")
        print(f"Processed words: {result.processed_data}")

if __name__ == "__main__":
    asyncio.run(main()) 