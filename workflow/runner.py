import time
from typing import Any, AsyncGenerator
from workflow.models import StepContext
from workflow.workflow import Workflow
from workflow.node import StepNode, ParallelNode
from workflow.event import (
    Event,
    WorkflowStartedEvent, WorkflowCompletedEvent,
    WorkflowFailedEvent
)

class Runner:
    """Base class for workflow execution runners."""
    
    def __init__(self, workflow: Workflow):
        self.workflow = workflow

    async def run_sync(self, input_data: Any) -> Any:
        """Run workflow synchronously and return the final result."""
        raise NotImplementedError("Subclasses must implement run_sync")
    
    async def run_streamed(self, input_data: Any) -> AsyncGenerator[Event, None]:
        """Run workflow and stream events about progress."""
        raise NotImplementedError("Subclasses must implement run_streamed")
    
class SystemRunner(Runner):
    """Standard workflow runner implementation."""
    
    def __init__(self, workflow: Workflow):
        super().__init__(workflow)
        self.input_schema = workflow.input_schema
    
    async def run_sync(self, input_data: Any) -> Any:
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
        nodes = self.workflow.nodes

        for node in nodes:
            context = StepContext(
                input_data=current_data,
                step_results=step_results,
                initial_data=validated_input,
                workflow_name=self.workflow.name
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
    
    async def run_streamed(self, input_data: Any) -> AsyncGenerator[Event, None]:
        """
        Execute the workflow and stream events about the execution progress.
        
        Args:
            input_data: The input data for the workflow
            
        Yields:
            Event objects indicating the progress of the workflow execution
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
            workflow_name=self.workflow.name,
            input_data=validated_input,
            output_data=None
        )
        current_data = validated_input
        
        try:
            # Process each node in sequence
            nodes = self.workflow.nodes
            for node in nodes:
                context = StepContext(
                    input_data=current_data,
                    step_results=step_results,
                    initial_data=validated_input,
                    workflow_name=self.workflow.name,
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