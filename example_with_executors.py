import asyncio
from typing import List, Dict

from workflow import (
    Step, Workflow, SystemRunner, StepContext, 
    AsyncIOExecutor, CeleryExecutor,
    UserInput, GreetingOutput, ProcessedOutput
)

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

async def analyze_data(input_data: GreetingOutput) -> dict:
    """Analyze the greeting data."""
    # Simulate some processing time
    await asyncio.sleep(1.5)
    
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
    await asyncio.sleep(2)
    
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

analyze_step = Step(
    name="Analyze Data",
    description="Analyzes the greeting data",
    input_schema=GreetingOutput,
    output_schema=dict,
    func=analyze_data
)

translate_step = Step(
    name="Translate Greeting",
    description="Translates the greeting to Spanish",
    input_schema=GreetingOutput,
    output_schema=dict,
    func=translate_greeting
)

# Create a sequential workflow
sequential_workflow = Workflow(
    name="Sequential Workflow",
    description="A sequential workflow with two steps",
    input_schema=UserInput
)
sequential_workflow.then(greeting_step).then(process_step)

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
    
    # Default AsyncIO executor (already used by default)
    async_runner = SystemRunner(sequential_workflow)
    async_result = await async_runner.run_sync(user_data)
    print(f"Sequential workflow result: {async_result}")
    
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
    
    # To use with Celery, uncomment the following code and set up Celery tasks
    """
    # Setup Celery (this would typically be in a separate module)
    from celery import Celery
    
    app = Celery('workflow_app', broker='pyamqp://guest@localhost//')
    
    # Decorator to convert async functions to Celery tasks
    def async_celery_task(func):
        @app.task
        def wrapper(*args, **kwargs):
            # Run the async function in a new event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(func(*args, **kwargs))
            loop.close()
            return result
        
        return wrapper
    
    # Register the functions as Celery tasks
    celery_greeting = async_celery_task(create_greeting)
    celery_process = async_celery_task(process_data)
    celery_analyze = async_celery_task(analyze_data)
    celery_translate = async_celery_task(translate_greeting)
    
    # Create new steps with Celery tasks
    greeting_celery_step = Step(
        name="Create Greeting (Celery)",
        description="Creates a personalized greeting message",
        input_schema=UserInput,
        output_schema=GreetingOutput,
        func=celery_greeting
    )
    
    process_celery_step = Step(
        name="Process Data (Celery)",
        description="Processes the greeting into structured data",
        input_schema=GreetingOutput,
        output_schema=ProcessedOutput,
        func=celery_process
    )
    
    analyze_celery_step = Step(
        name="Analyze Data (Celery)",
        description="Analyzes the greeting data",
        input_schema=GreetingOutput,
        output_schema=dict,
        func=celery_analyze
    )
    
    translate_celery_step = Step(
        name="Translate Greeting (Celery)",
        description="Translates the greeting to Spanish",
        input_schema=GreetingOutput,
        output_schema=dict,
        func=celery_translate
    )
    
    # Create Celery workflows
    celery_sequential_workflow = Workflow(
        name="Celery Sequential Workflow",
        description="A sequential workflow with Celery tasks",
        input_schema=UserInput
    )
    celery_sequential_workflow.then(greeting_celery_step).then(process_celery_step)
    
    celery_parallel_workflow = Workflow(
        name="Celery Parallel Workflow",
        description="A parallel workflow with Celery tasks",
        input_schema=UserInput
    )
    celery_parallel_workflow.then(greeting_celery_step).parallel([
        analyze_celery_step, translate_celery_step
    ])
    
    # Create Celery executor
    celery_executor = CeleryExecutor(app=app)
    
    # Run with Celery executor
    celery_runner = SystemRunner(celery_sequential_workflow, executor=celery_executor)
    celery_result = await celery_runner.run_sync(user_data)
    print(f"Celery sequential workflow result: {celery_result}")
    
    # Run parallel workflow with Celery
    celery_parallel_runner = SystemRunner(celery_parallel_workflow, executor=celery_executor)
    celery_parallel_result = await celery_parallel_runner.run_sync(user_data)
    print(f"Celery parallel workflow results:")
    for step_id, result in celery_parallel_result.items():
        print(f"  {step_id}: {result}")
    """

if __name__ == "__main__":
    asyncio.run(main()) 