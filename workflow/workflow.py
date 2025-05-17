from typing import  Generic, List, Type

from workflow.models import InputType, OutputType
from workflow.node import WorkflowNode, StepNode, ParallelNode
from workflow.step import Step


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
    
    def then(self, step: Step) -> "Workflow":
        """
        Add a step to be executed sequentially after the previous steps.
        
        Args:
            step: The step to add to the workflow
            
        Returns:
            The workflow instance for chaining
        """
        self.nodes.append(StepNode(step))
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