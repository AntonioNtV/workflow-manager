import time
from typing import Any, AsyncGenerator, Optional, Union
from pydantic import BaseModel
from uuid import UUID, uuid4

from v2.events.step import StepEventType
from v2.executor.asyncio import AsyncIOExecutor
from v2.executor.base import TaskExecutor
from v2.step.context import StepContext
from v2.workflow.workflow import Workflow
from v2.events import (
    WorkflowStartedEvent, WorkflowCompletedEvent, WorkflowFailedEvent, WorkflowEvent, StepEvent
)


class Runner:
    """Base class for workflow execution runners."""
    workflow: Workflow
    executor: TaskExecutor
    id: UUID
    
    def __init__(self, workflow: Workflow, executor: Optional[TaskExecutor] = None):
        """
        Initialize a workflow runner.
        
        Args:
            workflow: The workflow to run
            executor: The task executor to use (defaults to AsyncIOExecutor)
        """
        self.workflow = workflow
        self.executor = executor or AsyncIOExecutor()
        self.id = uuid4()
        
    async def run(self, input_data: BaseModel) -> Any:
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
        

        # Process each node in sequence
        current_data = validated_input
        for node in self.workflow.nodes:
            context = StepContext(
                input_data=current_data,
            )
            
            result = await node.execute(context=context, executor=self.executor)
            current_data = result

        return current_data
    
    async def run_with_events(self, input_data: BaseModel) -> AsyncGenerator[Union[WorkflowEvent, StepEvent], None]:
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
            workflow_id=str(self.id),
            workflow_name=self.workflow.name,
            input_data=validated_input
        )
        
        try:
            current_data = validated_input
            for node in self.workflow.nodes:
                context = StepContext(
                    input_data=current_data,
                )

                async for event in node.execute_with_events(context=context, executor=self.executor):
                    yield event

                    if event.type == StepEventType.STEP_COMPLETED:
                        current_data = event.output_data
                        
            yield WorkflowCompletedEvent(
                workflow_id=str(self.id),
                workflow_name=self.workflow.name,
            )
        except Exception as e:
            yield WorkflowFailedEvent(
                workflow_id=str(self.id),
                workflow_name=self.workflow.name,
                error=str(e),
            )
            raise