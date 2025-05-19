from typing import Callable, Type, Union
from pydantic import BaseModel, Field
from uuid import UUID, uuid4

class Step(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    func: Callable
    input_schema: Union[Type[BaseModel], Type[dict]]
    output_schema: Type[BaseModel]