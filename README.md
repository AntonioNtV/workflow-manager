# Python Workflow Manager

A simple, type-safe workflow orchestration library for Python that allows you to define, compose, and execute workflows with proper input/output validation.

## Features

- Define individual steps with clear input and output schemas using Pydantic
- Compose steps into workflows with an intuitive fluent API
- Support for sequential and parallel execution patterns
- Type safety throughout the workflow execution
- Resume capability for interrupted steps
- Streaming execution events for real-time monitoring

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Define Step Schemas

Use Pydantic models to define the input and output schemas for your steps:

```python
from pydantic import BaseModel

class UserInput(BaseModel):
    name: str
    age: int

class ProcessedUserData(BaseModel):
    user_id: str
    profile: dict
```

### Create Steps

Create individual steps by defining their input/output schemas and execution functions:

```python
from workflow import Step

process_step = Step(
    name="Process User Data",
    description="Processes raw user input and creates a user profile",
    input_schema=UserInput,
    output_schema=ProcessedUserData,
    func=process_user_data
)
```

### Build Workflows

Compose steps into workflows using the fluent API:

```python
from workflow import Workflow

user_onboarding = Workflow(
    name="User Onboarding",
    description="Onboards a new user and sends welcome notifications",
    input_schema=UserInput
)

# Define workflow execution pattern
user_onboarding.then(process_step).then(enrich_step).parallel([email_step, sms_step])
```

### Execute Workflows

Execute workflows with input data:

```python
# Create input data
input_data = UserInput(name="John Doe", age=25)

# Execute the workflow
result = await user_onboarding.execute(input_data)
```

### Stream Workflow Execution Events

For real-time monitoring of workflow execution, use the streaming API:

```python
# Execute workflow with streaming updates
async for event in workflow.run_streamed(input_data):
    if event.type == EventType.STEP_STARTED:
        print(f"Step '{event.step_name}' started")
    elif event.type == EventType.STEP_COMPLETED:
        print(f"Step '{event.step_name}' completed in {event.execution_time:.2f}s")
```

Available event types:
- `WORKFLOW_STARTED`: Emitted when the workflow begins execution
- `WORKFLOW_COMPLETED`: Emitted when the workflow finishes execution
- `STEP_STARTED`: Emitted when a step begins execution
- `STEP_COMPLETED`: Emitted when a step finishes execution

## Examples

- See `example.py` for a basic example of how to use the workflow manager
- See `streamed_example.py` for an example of streaming workflow execution events

## License

MIT 