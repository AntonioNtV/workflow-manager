import time
import asyncio
from typing import Any, AsyncGenerator, Dict, List, Optional

from workflow.models import StepContext
from workflow.workflow import Workflow
from workflow.node import StepNode, ParallelNode
from workflow.event import (
    Event, WorkflowStartedEvent, WorkflowCompletedEvent, WorkflowFailedEvent
)

class TaskExecutor:
    """Base class for workflow task execution backends."""
    
    async def execute_task(self, step, input_data: Any) -> Any:
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
    

class Runner:
    """Base class for workflow execution runners."""
    
    def __init__(self, workflow: Workflow, executor: Optional[TaskExecutor] = None):
        """
        Initialize a workflow runner.
        
        Args:
            workflow: The workflow to run
            executor: The task executor to use (defaults to AsyncIOExecutor)
        """
        self.workflow = workflow
        self.executor = executor or AsyncIOExecutor()

    async def run(self, input_data: Any) -> Any:
        """
        Run the workflow synchronously and return the final result.
        
        Args:
            input_data: The input data for the workflow
            
        Returns:
            The final output data from the workflow
        """
        # Validate input data
        validated_input = (
            self.workflow.input_schema.model_validate(input_data)
            if not isinstance(input_data, self.workflow.input_schema)
            else input_data
        )
        
        # Initialize step results storage
        step_results = {}
        
        # Process each node in sequence
        current_data = validated_input
        for node in self.workflow.nodes:
            context = StepContext(
                input_data=current_data,
                step_results=step_results,
                initial_data=validated_input,
                workflow_name=self.workflow.name
            )
            
            # Execute the node
            result = await node.execute(context, self.executor)

            current_data = result
            
            # Store step results
            if isinstance(node, StepNode):
                step_results[node.step.id] = result
            elif isinstance(node, ParallelNode) and isinstance(result, dict):
                step_results.update(result)
        
        return current_data
    
    async def run_with_events(self, input_data: Any) -> AsyncGenerator[Event, None]:
        """
        Run the workflow and stream events about the execution progress.
        
        Args:
            input_data: The input data for the workflow
            
        Yields:
            Event objects indicating the progress of the workflow execution
        """
        # Validate input data
        validated_input = (
            self.workflow.input_schema.model_validate(input_data)
            if not isinstance(input_data, self.workflow.input_schema)
            else input_data
        )
        
        # Initialize step results storage
        step_results = {}
        
        # Emit workflow started event
        start_time = time.time()
        yield WorkflowStartedEvent(
            workflow_name=self.workflow.name,
            input_data=validated_input
        )
        
        try:
            # Process each node in sequence
            current_data = validated_input
            for node in self.workflow.nodes:
                context = StepContext(
                    input_data=current_data,
                    step_results=step_results,
                    initial_data=validated_input,
                    workflow_name=self.workflow.name
                )

                # Execute the node with events
                async for event, data in node.execute_with_events(context, self.executor):
                    if event is not None:
                        current_data = data
                        yield event
                    else:
                        current_data = data
            
                # Store step results
                if isinstance(node, StepNode):
                    step_results[node.step.id] = current_data
                elif isinstance(node, ParallelNode) and isinstance(current_data, dict):
                    step_results.update(current_data)
            
            # Emit workflow completed event
            total_execution_time = time.time() - start_time
            yield WorkflowCompletedEvent(
                workflow_name=self.workflow.name,
                output_data=current_data,
                execution_time=total_execution_time
            )
        except Exception as e:
            # Emit workflow failed event
            total_execution_time = time.time() - start_time
            yield WorkflowFailedEvent(
                workflow_name=self.workflow.name,
                error=str(e),
                execution_time=total_execution_time
            )
            raise
