from typing import List, Type, Sequence
from pydantic import BaseModel

from v2.step import Step
from v2.workflow.node import WorkflowNode, StepNode, ParallelNode

class Workflow:

    """
    A workflow is a sequence of steps that can be executed in order.
    
    Workflows define a sequence of processing steps that transform
    an initial input into a final output, with steps organized to run
    either sequentially or in parallel.
    """
    name: str
    description: str
    input_schema: Type[BaseModel]
    nodes: List[WorkflowNode]
    
    def __init__(
        self,
        name: str,
        input_schema: Type[BaseModel],
        description: str = "",
    ):
        """
        Initialize a workflow.
        
        Args:
            name: The name of the workflow
            input_schema: The Pydantic model for validating the workflow input
            description: A description of what the workflow does
        """
        self.name = name
        self.description = description
        self.input_schema = input_schema
        self.nodes = []
        self._last_step_output_schema = input_schema
    
    def __add_step(self, step: Step) -> 'Workflow':
        """
        Add a single step to the workflow.
        
        Args:
            step: The step to add
            
        Returns:
            The workflow object for method chaining
        """
        # Validate that the step's input schema matches the previous step's output schema
        if step.input_schema != self._last_step_output_schema:
            raise ValueError(
                f"Step '{step.name}' input schema {step.input_schema} "
                f"doesn't match previous step's output schema {self._last_step_output_schema}"
            )
        
        # Add the step as a regular node
        self.nodes.append(StepNode(step))
        
        # Update the last step output schema
        self._last_step_output_schema = step.output_schema
        
        return self
    
    def __add_parallel_steps(self, steps: Sequence[Step]) -> 'Workflow':
        """
        Add multiple steps to be executed in parallel.
        
        All steps must accept the same input schema (matching the previous step's output),
        but can have different output schemas. The output will be a dictionary mapping
        step IDs to their results.
        
        Args:
            steps: The steps to add for parallel execution
            
        Returns:
            The workflow object for method chaining
        """
        if not steps:
            raise ValueError("No steps provided for parallel execution")
        
        # Validate that all steps have the same input schema, matching the previous step's output schema
        for step in steps:
            if step.input_schema != self._last_step_output_schema:
                raise ValueError(
                    f"Step '{step.name}' input schema {step.input_schema} "
                    f"doesn't match previous step's output schema {self._last_step_output_schema}"
                )
        
        self.nodes.append(ParallelNode(steps))
        
        # The output schema of a parallel node is a dict of step IDs to results
        self._last_step_output_schema = dict
        
        return self
    
    # Convenient aliases
    def then(self, step: Step) -> 'Workflow':
        """Alias for add_step."""
        return self.__add_step(step)
    
    def parallel(self, steps: Sequence[Step]) -> 'Workflow':
        """Alias for add_parallel_steps."""
        return self.__add_parallel_steps(steps)