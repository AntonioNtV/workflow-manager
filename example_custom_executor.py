import asyncio
import logging
from typing import Any, List, Dict

from workflow import (
    Step, Workflow, Runner, TaskExecutor,
    UserInput, GreetingOutput, ProcessedOutput
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Define a custom task executor
class LoggingExecutor(TaskExecutor):
    """Task executor that logs execution details."""
    
    def __init__(self, log_level=logging.INFO):
        self.log_level = log_level
    
    async def execute_task(self, func, *args, **kwargs) -> Any:
        """Execute a single task with logging."""
        func_name = getattr(func, "__name__", str(func))
        logger.log(self.log_level, f"Starting task {func_name}")
        
        start_time = asyncio.get_event_loop().time()
        result = await super().execute_task(func, *args, **kwargs)
        end_time = asyncio.get_event_loop().time()
        
        execution_time = end_time - start_time
        logger.log(self.log_level, f"Completed task {func_name} in {execution_time:.2f}s")
        
        return result
    
    async def execute_tasks_parallel(self, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute multiple tasks in parallel with logging."""
        task_ids = [task["id"] for task in tasks]
        logger.log(self.log_level, f"Starting parallel execution of {len(tasks)} tasks: {task_ids}")
        
        start_time = asyncio.get_event_loop().time()
        results = await super().execute_tasks_parallel(tasks)
        end_time = asyncio.get_event_loop().time()
        
        execution_time = end_time - start_time
        logger.log(self.log_level, f"Completed parallel execution in {execution_time:.2f}s")
        
        return results

# Define step functions
async def create_greeting(input_data: UserInput) -> GreetingOutput:
    """Generate a personalized greeting."""
    await asyncio.sleep(1)  # Simulate processing time
    message = f"Hello {input_data.name}, you are {input_data.age} years old!"
    return GreetingOutput(message=message)

async def process_data(input_data: GreetingOutput) -> ProcessedOutput:
    """Process the greeting into a structured format."""
    await asyncio.sleep(1)  # Simulate processing time
    words = input_data.message.split()
    return ProcessedOutput(
        original_message=input_data.message,
        processed_data=words
    )

async def analyze_greeting(input_data: GreetingOutput) -> dict:
    """Analyze the greeting message."""
    await asyncio.sleep(1)  # Simulate processing time
    
    char_count = len(input_data.message)
    word_count = len(input_data.message.split())
    
    return {
        "character_count": char_count,
        "word_count": word_count,
        "has_numbers": any(c.isdigit() for c in input_data.message)
    }

# Create workflow steps
greeting_step = Step(
    name="Create Greeting",
    func=create_greeting,
    input_schema=UserInput,
    output_schema=GreetingOutput,
    description="Creates a personalized greeting message"
)

process_step = Step(
    name="Process Data",
    func=process_data,
    input_schema=GreetingOutput,
    output_schema=ProcessedOutput,
    description="Processes the greeting into structured data"
)

analyze_step = Step(
    name="Analyze Greeting",
    func=analyze_greeting,
    input_schema=GreetingOutput,
    output_schema=dict,
    description="Analyzes the greeting message"
)

# Create the workflow with parallel steps
workflow = Workflow(
    name="Custom Executor Workflow",
    input_schema=UserInput,
    description="A workflow with a custom logging executor"
)
workflow.then(greeting_step).parallel([process_step, analyze_step])

# Run the workflow with the custom executor
async def main():
    # Input data
    user_data = UserInput(name="Alice", age=30)
    
    # Create a custom logging executor
    logging_executor = LoggingExecutor(log_level=logging.INFO)
    
    # Create and run the workflow with the custom executor
    runner = Runner(workflow, executor=logging_executor)
    
    print("=" * 50)
    print("Running workflow with custom LoggingExecutor")
    print("=" * 50)
    
    # Run the workflow
    result = await runner.run(user_data)
    
    print("=" * 50)
    print(f"Final result:")
    for step_id, value in result.items():
        print(f"  {step_id}: {value}")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(main()) 