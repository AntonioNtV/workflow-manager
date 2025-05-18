import asyncio
from pydantic import BaseModel
from typing import List

from workflow import Step, Workflow, Runner
from models import UserInput, GreetingOutput, ProcessedOutput

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
    message = f"Hello {input_data.name}, you are {input_data.age} years old!"
    return GreetingOutput(message=message)

async def process_data(input_data: GreetingOutput) -> ProcessedOutput:
    """Process the greeting into a structured format."""
    # Split the message into words
    words = input_data.message.split()
    return ProcessedOutput(
        original_message=input_data.message,
        processed_data=words
    )

# Create workflow steps
greeting_step = Step(
    id="create_greeting",
    name="Create Greeting",
    func=create_greeting,
    input_schema=UserInput,
    output_schema=GreetingOutput,
    description="Creates a personalized greeting message"
)

process_step = Step(
    id="process_data",
    name="Process Data",
    func=process_data,
    input_schema=GreetingOutput,
    output_schema=ProcessedOutput,
    description="Processes the greeting into structured data"
)

# Create the workflow
workflow = Workflow(
    name="Greeting Workflow",
    input_schema=UserInput,
    description="A simple workflow that creates and processes a greeting"
)

# Add steps to the workflow
workflow.then(greeting_step).then(process_step)

# Run the workflow
async def main():
    # Create a runner
    runner = Runner(workflow)
    
    # Input data
    user_data = UserInput(name="Alice", age=30)
    
    # Run the workflow
    result = await runner.run(user_data)
    
    # Print the results
    print(f"Workflow result: {result}")
    print(f"Original message: {result.original_message}")
    print(f"Processed words: {result.processed_data}")

if __name__ == "__main__":
    asyncio.run(main()) 