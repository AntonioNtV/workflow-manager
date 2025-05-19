import asyncio
from typing import Any, Dict, List, Tuple, Type
from uuid import UUID
from pydantic import BaseModel
from v2.step import Step
from v2.step.context import StepContext

class TaskExecutor:
    """Base class for workflow task execution backends."""
    
    async def execute_task(self, step: Step, context: StepContext) -> Any:
        """Execute a single task using the executor.
        
        Args:
            step: The Step object to execute
            context: The context for the step
        """
        return await step.func(context.input_data)
    
    async def execute_tasks_parallel(self, steps: List[Step], context: StepContext) -> Dict[str, Any]:
        """Execute multiple tasks in parallel using the executor.
        
        Args:
            steps_with_data: List of dictionaries containing:
                - "step": The Step object to execute
                - "id": The task ID
                - "input_data": The input data for the step
        """
        results = {}
        coroutines = []
        
        for step in steps:
            task_id = step.id
            step = step
            input_data = context.input_data
            
            coroutines.append(self._run_and_store(task_id, step, input_data))
        
        # Run all coroutines in parallel
        completed = await asyncio.gather(*coroutines)
        
        # Store results by task ID
        for task_id, result in completed:
            results[task_id] = result
            
        return results
    
    async def _run_and_store(self, task_id: UUID, step: Step, input_data: Any) -> Tuple[UUID, Type[BaseModel]]:
        """Helper method to run a task and return its ID with the result."""
        result = await step.execute(input_data)
        return (task_id, result)
