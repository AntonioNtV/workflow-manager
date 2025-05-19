from typing import Any, Dict, List, AsyncGenerator, Sequence
import time

from workflow.models import StepContext
from workflow.event import (
    Event, StepStartedEvent, StepCompletedEvent
)
from workflow.step import Step
from workflow.executor import TaskExecutor

class WorkflowNode:
    """Base class for a node in the workflow execution graph."""
    
    async def execute(self, context: StepContext, executor: TaskExecutor = None) -> Any:
        """Execute this node and return the result."""
        raise NotImplementedError("Subclasses must implement execute")
    
    async def execute_with_events(self, context: StepContext, executor: TaskExecutor = None) -> AsyncGenerator[tuple[Event, Any], None]:
        """Execute this node and yield events along with the updated data."""
        raise NotImplementedError("Subclasses must implement execute_with_events")


class StepNode(WorkflowNode):
    """A workflow node that represents a single step execution."""
    
    def __init__(self, step: Step):
        self.step = step
    
    async def execute(self, context: StepContext, executor: TaskExecutor = None) -> Any:
        """Execute the step and return its result."""
        if executor:
            result = await executor.execute_task(self.step, context.input_data)
        else:
            result = await self.step.execute(context.input_data)
        return result
    
    async def execute_with_events(self, context: StepContext, executor: TaskExecutor = None) -> AsyncGenerator[tuple[Event, Any], None]:
        """Execute the step and yield execution events."""
        step = self.step
        step_start_time = time.time()
        
        # Emit step started event
        yield (StepStartedEvent(
            workflow_name=context.workflow_name,
            step_id=step.id,
            step_name=step.name,
            input_data=context.input_data,
        ), context.input_data)
        
        # Execute the step
        result = await self.execute(context, executor)
                
        # Emit step completed event
        step_execution_time = time.time() - step_start_time
        yield (StepCompletedEvent(
            workflow_name=context.workflow_name,
            step_id=step.id,
            step_name=step.name,
            output_data=result,
            execution_time=step_execution_time
        ), result)


class ParallelNode(WorkflowNode):
    """A workflow node that represents parallel execution of multiple steps."""
    
    def __init__(self, steps: Sequence[Step]):
        self.steps = steps
    
    async def execute(self, context: StepContext, executor: TaskExecutor = None) -> Dict[str, Any]:
        """Execute all steps in parallel and return a dictionary of results."""
            # Use the executor for parallel execution
        parallel_tasks = [
            {
                "id": step.id,
                "step": step,
                "input_data": context.input_data,
            }
            for step in self.steps
        ]
        return await executor.execute_tasks_parallel(parallel_tasks)

    
    async def execute_with_events(self, context: StepContext, executor: TaskExecutor = None) -> AsyncGenerator[tuple[Event, Any], None]:
        """Execute all steps in parallel and yield execution events."""
        # Emit started events for all steps first
        for step in self.steps:
            yield (StepStartedEvent(
                workflow_name=context.workflow_name,
                step_id=step.id,
                step_name=step.name,
                input_data=context.input_data,
            ), context.input_data)
        
        # Execute all steps 
        step_start_time = time.time()
        results = await self.execute(context, executor)
        step_execution_time = time.time() - step_start_time
        
        # Emit completed events for all steps
        for step in self.steps:
            result = results[step.id]
            yield (StepCompletedEvent(
                workflow_name=context.workflow_name,
                step_id=step.id,
                step_name=step.name,
                output_data=result,
                execution_time=step_execution_time
            ), context.input_data)
        
        # Return the collected results
        yield (None, results) 