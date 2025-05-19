
import asyncio
from typing import Any, Dict, List
from workflow.step import Step


class TaskExecutor:
    """Base class for workflow task execution backends."""
    
    async def execute_task(self, step: Step, input_data: Any) -> Any:
        """Execute a single task using the executor.
        
        Args:
            step: The Step object to execute
            input_data: The input data for the step
        """
        return await step.execute(input_data)
    
    async def execute_tasks_parallel(self, steps_with_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute multiple tasks in parallel using the executor.
        
        Args:
            steps_with_data: List of dictionaries containing:
                - "step": The Step object to execute
                - "id": The task ID
                - "input_data": The input data for the step
        """
        results = {}
        coroutines = []
        
        for task in steps_with_data:
            task_id = task["step"].id
            step = task["step"]
            input_data = task["input_data"]
            
            coroutines.append(self._run_and_store(task_id, step, input_data))
        
        # Run all coroutines in parallel
        completed = await asyncio.gather(*coroutines)
        
        # Store results by task ID
        for task_id, result in completed:
            results[task_id] = result
            
        return results
    
    async def _run_and_store(self, task_id: str, step, input_data: Any) -> tuple:
        """Helper method to run a task and return its ID with the result."""
        result = await step.execute(input_data)
        return (task_id, result)


class AsyncIOExecutor(TaskExecutor):
    """Task executor that uses asyncio for execution."""
    pass  # Uses default TaskExecutor implementation
    