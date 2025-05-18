import asyncio

from workflow import (
    Step, Workflow, SystemRunner, 
)

from models import UserInput, GreetingOutput

# Define step functions
async def create_greeting(input_data: UserInput) -> GreetingOutput:
    """Generate a personalized greeting."""
    # Simulate some processing time
    await asyncio.sleep(1)
    message = f"Hello {input_data.name}, you are {input_data.age} years old!"
    return GreetingOutput(message=message)

async def analyze_data(input_data: GreetingOutput) -> dict:
    """Analyze the greeting data."""
    # Simulate some processing time
    print("Analyzing data...")
    await asyncio.sleep(20)
    
    # Count characters and words
    char_count = len(input_data.message)
    word_count = len(input_data.message.split())
    
    return {
        "character_count": char_count,
        "word_count": word_count,
        "has_numbers": any(c.isdigit() for c in input_data.message)
    }

async def translate_greeting(input_data: GreetingOutput) -> dict:
    """Translate the greeting to Spanish."""
    # Simulate some processing time
    print("Translating greeting...")
    await asyncio.sleep(20)
    
    # Simple translation logic for demonstration
    parts = input_data.message.split(", ")
    if len(parts) == 2:
        name_part = parts[0].replace("Hello ", "Hola ")
        age_part = parts[1].replace("you are ", "tienes ").replace(" years old!", " años!")
        spanish = f"{name_part}, {age_part}"
    else:
        spanish = "Hola!"
    
    return {
        "original": input_data.message,
        "spanish": spanish
    }

# Create workflow steps
greeting_step = Step(
    id="create_greeting",
    name="Create Greeting",
    description="Creates a personalized greeting message",
    input_schema=UserInput,
    output_schema=GreetingOutput,
    func=create_greeting
)

analyze_step = Step(
    id="analyze_data",
    name="Analyze Data",
    description="Analyzes the greeting data",
    input_schema=GreetingOutput,
    output_schema=dict,
    func=analyze_data
)

translate_step = Step(
    id="translate_greeting",
    name="Translate Greeting",
    description="Translates the greeting to Spanish",
    input_schema=GreetingOutput,
    output_schema=dict,
    func=translate_greeting
)

# Create a parallel workflow
parallel_workflow = Workflow(
    name="Parallel Processing Workflow",
    description="A workflow with parallel steps",
    input_schema=UserInput
)
parallel_workflow.then(greeting_step).parallel([analyze_step, translate_step])

# Run the workflows with different executors
async def main():
    # Input data
    user_data = UserInput(name="Alice", age=30)
    
    print("=" * 50)
    print("Running with AsyncIO Executor (Default)")
    print("=" * 50)
    
    # Run parallel workflow with AsyncIO executor
    async_parallel_runner = SystemRunner(parallel_workflow)
    async_parallel_result = await async_parallel_runner.run_sync(user_data)

    print(f"Parallel workflow results:")
    for step_id, result in async_parallel_result.items():
        print(f"  {step_id}: {result}")
    
    print("\n" + "=" * 50)
    print("Running with Celery Executor (commented out)")
    print("=" * 50)
    print("To use Celery, uncomment the code below and ensure Celery is installed and configured")



if __name__ == "__main__":
    asyncio.run(main()) 