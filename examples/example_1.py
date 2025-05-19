from pydantic import BaseModel
import asyncio
import sys
import os

# Add the project root directory to Python's path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from v2.workflow.workflow import Workflow
from v2.step.step import Step
from v2.workflow.runner import Runner


# Define input and output schemas for steps
class InputData(BaseModel):
    text: str

class ProcessedData(BaseModel):
    text: str
    word_count: int

class FinalOutput(BaseModel):
    text: str
    word_count: int
    character_count: int


# Define step functions
async def count_words(data: InputData) -> ProcessedData:
    word_count = len(data.text.split())
    return ProcessedData(text=data.text, word_count=word_count)

async def count_characters(data: ProcessedData) -> FinalOutput:
    character_count = len(data.text)
    return FinalOutput(
        text=data.text,
        word_count=data.word_count,
        character_count=character_count
    )


# Create steps
step1 = Step(
    name="Count Words",
    func=count_words,
    input_schema=InputData,
    output_schema=ProcessedData
)

step2 = Step(
    name="Count Characters",
    func=count_characters,
    input_schema=ProcessedData,
    output_schema=FinalOutput
)


# Define the workflow
text_analysis_workflow = Workflow(
    name="Text Analysis",
    input_schema=InputData,
    description="A workflow that analyzes text by counting words and characters"
)

# Add steps to the workflow
text_analysis_workflow.then(step1).then(step2)


# Run the workflow
async def main():
    # Initialize the runner
    runner = Runner(workflow=text_analysis_workflow)
    
    # Prepare input data
    input_data = InputData(text="Hello, this is a simple example of a workflow!")
    
    # Run the workflow
    result = await runner.run(input_data)
    
    # Display the result
    print(f"Original text: {result.text}")
    print(f"Word count: {result.word_count}")
    print(f"Character count: {result.character_count}")
    
    # Alternatively, run with events to see the workflow progress
    print("\nRunning with events:")
    async for event in runner.run_with_events(input_data):
        print(event)

if __name__ == "__main__":
    asyncio.run(main())
