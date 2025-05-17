from typing import Any, Dict, List, AsyncGenerator
import time

from workflow.models import StepContext
from workflow.event import (
    Event, StepStartedEvent, StepCompletedEvent
)
from workflow.step import Step


class WorkflowNode:
    """Base class for a node in the workflow execution graph."""
    
    async def execute_node(self, context: StepContext) -> Any:
        """Execute this node and return the result"""
        raise NotImplementedError("Subclasses must implement execute_node")
    
    async def execute_with_events(self, context: StepContext) -> AsyncGenerator[tuple[Event, Any], None]:
        """Execute this node and yield events along with the updated data"""
        raise NotImplementedError("Subclasses must implement execute_with_events")


class StepNode(WorkflowNode):
    """A workflow node that represents a single step execution."""
    
    def __init__(self, step: Step):
        self.step = step
    
    async def execute_node(self, context: StepContext) -> Any:
        result = await self.step.execute(context)
        return result
    
    async def execute_with_events(self, context: StepContext) -> AsyncGenerator[tuple[Event, Any], None]:
        step = self.step
        step_start_time = time.time()
        
        # Emit step started event
        yield (StepStartedEvent(
            workflow_name=context.workflow_name,
            step_id=step.id,
            step_name=step.name,
            input_data=context.input_data,
            output_data=None
        ), context.input_data)
        
        # Execute the step
        print(f"Executing step {step.name} with context: {context}")
        result = await self.step.execute(context)
                
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
    
    def __init__(self, steps: List[Step]):
        self.steps = steps
    
    async def execute_node(self, context: StepContext) -> Dict[str, Any]:
        results = {}
        for step in self.steps:
            # Create a clone of the context for each parallel step
            step_context = StepContext(
                input_data=context.input_data,
                step_results=context.step_results.copy(),
                initial_data=context.initial_data,
                workflow_name=context.workflow_name
            )
            result = await step.execute(step_context)
            results[step.id] = result
        return results
    
    async def execute_with_events(self, context: StepContext) -> AsyncGenerator[tuple[Event, Any], None]:
        results = {}
        
        # In a production implementation, we would use asyncio.gather with proper
        # concurrency control and event emission
        for step in self.steps:
            step_start_time = time.time()
              
            # Emit step started event
            yield (StepStartedEvent(
                workflow_name=context.workflow_name,
                step_id=step.id,
                step_name=step.name,
                input_data=context.input_data,
                output_data=None
            ), context.input_data)
            
            # Execute the step
            result = await step.execute(context=context)
            results[step.id] = result
            
            # Emit step completed event
            step_execution_time = time.time() - step_start_time

            yield (StepCompletedEvent(
                workflow_name=context.workflow_name,
                step_id=step.id,
                step_name=step.name,
                output_data=result,
                execution_time=step_execution_time
            ), context.input_data)
        
        # Return the collected results
        yield (None, results) 