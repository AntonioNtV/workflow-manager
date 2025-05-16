from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union, AsyncGenerator, Callable
from pydantic import BaseModel
from enum import Enum
import time
import asyncio

from workflow.step import Step
from workflow.context import StepContext

InputType = TypeVar("InputType", bound=BaseModel)
OutputType = TypeVar("OutputType", bound=BaseModel)


class EventType(Enum):
    STEP_STARTED = "step_started"
    STEP_COMPLETED = "step_completed"
    WORKFLOW_STARTED = "workflow_started"
    WORKFLOW_COMPLETED = "workflow_completed"


class WorkflowEvent(BaseModel):
    """Base class for workflow execution events."""
    type: EventType
    workflow_name: str
    output_data: Optional[Any] = None


class StepEvent(WorkflowEvent):
    """Event for step execution updates."""
    step_id: str
    step_name: str


class StepStartedEvent(StepEvent):
    """Event emitted when a step starts executing."""
    type: EventType = EventType.STEP_STARTED
    input_data: Any
    output_data: Optional[Any] = None


class StepCompletedEvent(StepEvent):
    """Event emitted when a step completes execution."""
    type: EventType = EventType.STEP_COMPLETED
    output_data: Any
    execution_time: float


class WorkflowStartedEvent(WorkflowEvent):
    """Event emitted when the workflow starts executing."""
    type: EventType = EventType.WORKFLOW_STARTED
    input_data: Any
    output_data: Optional[Any] = None


class WorkflowCompletedEvent(WorkflowEvent):
    """Event emitted when the workflow completes execution."""
    type: EventType = EventType.WORKFLOW_COMPLETED
    output_data: Any
    execution_time: float


class WorkflowNode:
    """Base class for a node in the workflow execution graph."""
    
    async def execute_node(self, context: StepContext) -> Any:
        """Execute this node and return the result"""
        raise NotImplementedError("Subclasses must implement execute_node")
    
    async def execute_with_events(self, context: StepContext) -> AsyncGenerator[tuple[WorkflowEvent, Any], None]:
        """Execute this node and yield events along with the updated data"""
        raise NotImplementedError("Subclasses must implement execute_with_events")


class StepNode(WorkflowNode):
    """A workflow node that represents a single step execution."""
    
    def __init__(self, step: Step):
        self.step = step
    
    async def execute_node(self,context: StepContext) -> Any:
        result = await self.step.execute(context)
        return result
    
    async def execute_with_events(self, context: StepContext) -> AsyncGenerator[tuple[WorkflowEvent, Any], None]:
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
        result = await step.execute(context)
                
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
    
    async def execute_with_events(self, context: StepContext) -> AsyncGenerator[tuple[WorkflowEvent, Any], None]:
        results = {}
        
        # In a production implementation, we would use asyncio.gather with proper
        # concurrency control and event emission
        for step in self.steps:
            step_start_time = time.time()
            
            # Create a clone of the context for each parallel step
            step_context = StepContext(
                input_data=context.input_data,
                step_results=context.step_results.copy(),
                initial_data=context.initial_data,
                workflow_name=context.workflow_name
            )
            
            # Emit step started event
            yield (StepStartedEvent(
                workflow_name=context.workflow_name,
                step_id=step.id,
                step_name=step.name,
                input_data=context.input_data,
                output_data=None
            ), context.input_data)
            
            # Execute the step
            result = await step.execute(step_context)
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


class Workflow(Generic[InputType, OutputType]):
    """
    A Workflow orchestrates the execution of Steps with defined execution patterns.
    
    Attributes:
        name: The name of the workflow
        description: A brief description of what the workflow does
        input_schema: The Pydantic model class for workflow inputs
        nodes: The execution graph of the workflow
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        input_schema: Type[InputType],
    ):
        self.name = name
        self.description = description
        self.input_schema = input_schema
        self.nodes: List[WorkflowNode] = []
        self._last_output_schema = input_schema
    
    def then(self, step: Step) -> "Workflow":
        """
        Add a step to be executed sequentially after the previous steps.
        
        Args:
            step: The step to add to the workflow
            
        Returns:
            The workflow instance for chaining
        """
        self.nodes.append(StepNode(step))
        self._last_output_schema = step.output_schema
        return self
    
    def parallel(self, steps: List[Step]) -> "Workflow":
        """
        Add steps to be executed in parallel.
        
        Args:
            steps: The steps to execute in parallel
            
        Returns:
            The workflow instance for chaining
        """
        self.nodes.append(ParallelNode(steps))
        # Parallel execution results in a dictionary of {step_id: step_output}
        return self
    
    async def execute(self, input_data: Any) -> Any:
        """
        Execute the workflow with the given input data.
        
        Args:
            input_data: The input data for the workflow
            
        Returns:
            The output data from the workflow
        """
        # Validate input data
        validated_input = (
            self.input_schema.model_validate(input_data)
            if not isinstance(input_data, self.input_schema)
            else input_data
        )
        
        # Initialize step results storage
        step_results = {}
        
        current_data = validated_input
        
        for node in self.nodes:
            context = StepContext(
                input_data=current_data,
                step_results=step_results,
                initial_data=validated_input,
                workflow_name=self.name
            )
            
            result = await node.execute_node(context)
            current_data = result
            # Store results from this node
            if isinstance(node, StepNode):
                step_results[node.step.id] = result
            elif isinstance(node, ParallelNode):
                # For parallel nodes, results is a dict of {step_id: result}
                step_results.update(result)
        
        return current_data
    
    async def run_streamed(self, input_data: Any) -> AsyncGenerator[WorkflowEvent, None]:
        """
        Execute the workflow and stream events about the execution progress.
        
        Args:
            input_data: The input data for the workflow
            
        Yields:
            WorkflowEvent objects indicating the progress of the workflow execution
        """
        # Validate input data
        validated_input = (
            self.input_schema.model_validate(input_data)
            if not isinstance(input_data, self.input_schema)
            else input_data
        )
        
        # Initialize step results storage
        step_results = {}
        
        # Emit workflow started event
        start_time = time.time()
        yield WorkflowStartedEvent(
            workflow_name=self.name,
            input_data=validated_input,
            output_data=None
        )
        current_data = validated_input
        
        # Process each node in sequence

        for node in self.nodes:
            context = StepContext(
                input_data=current_data,
                step_results=step_results,
                initial_data=validated_input,
                workflow_name=self.name
            )
        
            
            async for event, data in node.execute_with_events(context):
                if event is not None:  # Skip None events (used for internal data passing)
                    yield event
                else:
                    current_data = data
            
            # If the last yielded item was an event (not None), update current_data
            if 'data' in locals():
                current_data = data
                
                # Store results from this node
                if isinstance(node, StepNode):
                    step_results[node.step.id] = current_data
                elif isinstance(node, ParallelNode) and isinstance(current_data, dict):
                    # For parallel nodes, current_data is a dict of {step_id: result}
                    step_results.update(current_data)
        
        # Emit workflow completed event
        total_execution_time = time.time() - start_time
        yield WorkflowCompletedEvent(
            workflow_name=self.name,
            output_data=current_data,
            execution_time=total_execution_time
        ) 