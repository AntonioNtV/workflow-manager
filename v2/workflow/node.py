from typing import Any, Dict, AsyncGenerator, Sequence
import time

from v2.executor.base import TaskExecutor
from v2.step.context import StepContext
from v2.events.step import StepStartedEvent, StepCompletedEvent, StepEvent
from v2.step import Step

class WorkflowNode:
    """Base class for a node in the workflow execution graph."""
    
    async def execute(self, context: StepContext, executor: TaskExecutor) -> Any:
        """Execute this node and return the result."""
        raise NotImplementedError("Subclasses must implement execute")
    
    async def execute_with_events(self, context: StepContext, executor: TaskExecutor) -> AsyncGenerator[StepEvent, None]:
        """Execute this node and yield events along with the updated data."""
        raise NotImplementedError("Subclasses must implement execute_with_events")


class StepNode(WorkflowNode):
    """A workflow node that represents a single step execution."""
    
    def __init__(self, step: Step):
        self.step = step
    
    async def execute(self, context: StepContext, executor: TaskExecutor) -> Any:
        return await executor.execute_task(self.step, context)
    
    async def execute_with_events(self, context: StepContext, executor: TaskExecutor) -> AsyncGenerator[StepEvent, None]:
        """Execute the step and yield execution events."""
        step = self.step
        
        # Emit step started event
        yield StepStartedEvent(
            step_id=step.id,
            step_name=step.name,
            input_data=context.input_data,
        )
        
        # Execute the step
        result = await self.execute(context, executor)
                
        # Emit step completed event
        yield StepCompletedEvent(
            step_id=step.id,
            step_name=step.name,
            output_data=result,
        )


class ParallelNode(WorkflowNode):
    """A workflow node that represents parallel execution of multiple steps."""
    
    def __init__(self, steps: Sequence[Step]):
        self.steps = steps
    
    async def execute(self, context: StepContext, executor: TaskExecutor) -> Dict[str, Any]:
        """Execute all steps in parallel and return a dictionary of results."""
        return await executor.execute_tasks_parallel(self.steps, context)
    
    
    async def execute_with_events(self, context: StepContext, executor: TaskExecutor) -> AsyncGenerator[StepEvent, None]:
        """Execute all steps in parallel and yield execution events."""
        # Emit started events for all steps first
        for step in self.steps:
            yield StepStartedEvent(
                step_id=step.id,
                step_name=step.name,
                input_data=context.input_data,
            )
        
        # Execute all steps 
        results = await self.execute(context, executor)
        
        # Emit completed events for all steps
        for step in self.steps:
            result = results[step.id]
            yield StepCompletedEvent(
                step_id=step.id,
                step_name=step.name,
                output_data=result,
            )