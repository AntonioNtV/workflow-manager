import asyncio
from typing import Dict, List, Optional, Any
from pydantic import BaseModel

from workflow import Step, Workflow
from workflow.workflow import EventType, WorkflowEvent, StepStartedEvent, StepCompletedEvent, StepContext


# Define input and output schemas for steps
class UserInput(BaseModel):
    name: str
    age: int


class ProcessedUserData(BaseModel):
    user_id: str
    profile: Dict[str, Any]


class EnrichedUserData(BaseModel):
    user_id: str
    profile: Dict[str, Any]
    preferences: List[str]


class NotificationResult(BaseModel):
    user_id: str
    notification_sent: bool
    channel: str
    original_name: Optional[str] = None  # Will be populated from initial data


# Define step functions
async def process_user_data(context: StepContext, resume_data=None):
    """Process initial user data and create a user profile."""
    user_input = context.input_data
    
    # Create a user ID and basic profile
    user_id = f"user_{user_input.name.lower().replace(' ', '_')}_{user_input.age}"
    profile = {
        "name": user_input.name,
        "age": user_input.age,
        "created_at": "2023-05-20T14:30:00Z"
    }
    
    # Simulate processing delay
    await asyncio.sleep(1.0)
    
    return ProcessedUserData(user_id=user_id, profile=profile)


async def enrich_user_data(context: StepContext, resume_data=None):
    """Enrich user data with additional information."""
    processed_data = context.input_data
    
    # Access the initial data to demonstrate context usage
    initial_data = context.get_initial_data()
    print(f"   [Enrichment] Original user name: {initial_data.name}")
    
    # Add preferences based on user age
    if processed_data.profile["age"] < 18:
        preferences = ["games", "music", "education"]
    elif processed_data.profile["age"] < 30:
        preferences = ["travel", "tech", "sports"]
    else:
        preferences = ["news", "cooking", "health"]
    
    # Simulate processing delay
    await asyncio.sleep(0.8)
    
    return EnrichedUserData(
        user_id=processed_data.user_id,
        profile=processed_data.profile,
        preferences=preferences
    )


async def send_email_notification(context: StepContext, resume_data=None):
    """Send email notification to the user."""
    user_data = context.input_data
    
    # Access the initial user input from the workflow context
    initial_data = context.get_initial_data()
    
    # Access the processed data step's result using the step ID
    try:
        # Step ID is based on the step name: "process user data" -> "process_user_data"
        process_step_result = context.get_step_result("process_user_data")
        print(f"   [Email] Using process step result: {process_step_result.user_id}")
    except KeyError as e:
        # Print available step IDs for debugging
        print(f"   [Email] Process step result not found. Available steps: {list(context.step_results.keys())}")
    
    # Simulate sending an email
    await asyncio.sleep(0.5)
    
    return NotificationResult(
        user_id=user_data.user_id,
        notification_sent=True,
        channel="email",
        original_name=initial_data.name  # Use initial data
    )


async def send_sms_notification(context: StepContext, resume_data=None):
    """Send SMS notification to the user."""
    user_data = context.input_data
    
    # Access the initial user input from the workflow context
    initial_data = context.get_initial_data()
    
    # Access the enriched data to demonstrate context usage
    try:
        # Step ID is based on the step name: "enrich user data" -> "enrich_user_data"
        enrich_step_result = context.get_step_result("enrich_user_data")
        print(f"   [SMS] Using preferences from enrich step: {enrich_step_result.preferences}")
    except KeyError:
        # Print available step IDs for debugging
        print(f"   [SMS] Enrich step result not found. Available steps: {list(context.step_results.keys())}")
    
    # Simulate sending an SMS
    await asyncio.sleep(0.3)
    
    return NotificationResult(
        user_id=user_data.user_id,
        notification_sent=True,
        channel="sms",
        original_name=initial_data.name  # Use initial data
    )


async def handle_workflow_event(event: WorkflowEvent):
    """Handle workflow execution events."""
    if event.type == EventType.WORKFLOW_STARTED:
        print(f"🚀 Workflow '{event.workflow_name}' started")
        
    elif event.type == EventType.WORKFLOW_COMPLETED:
        print(f"✅ Workflow '{event.workflow_name}' completed in {event.execution_time:.2f}s")
        
    elif event.type == EventType.STEP_STARTED:
        print(f"▶️  Step '{event.step_name}' started")
        
    elif event.type == EventType.STEP_COMPLETED:
        print(f"✓  Step '{event.step_name}' completed in {event.execution_time:.2f}s")


async def main():
    # Create steps with explicit IDs for easy reference
    process_step = Step(
        name="Process User Data",
        description="Processes raw user input and creates a user profile",
        input_schema=UserInput,
        output_schema=ProcessedUserData,
        func=process_user_data
    )
    # Print the generated step ID for debugging
    print(f"Process step ID: {process_step.id}")
    
    enrich_step = Step(
        name="Enrich User Data",
        description="Enriches user data with additional information",
        input_schema=ProcessedUserData,
        output_schema=EnrichedUserData,
        func=enrich_user_data
    )
    # Print the generated step ID for debugging
    print(f"Enrich step ID: {enrich_step.id}")
    
    email_step = Step(
        name="Send Email Notification",
        description="Sends an email notification to the user",
        input_schema=EnrichedUserData,
        output_schema=NotificationResult,
        func=send_email_notification
    )
    
    sms_step = Step(
        name="Send SMS Notification",
        description="Sends an SMS notification to the user",
        input_schema=EnrichedUserData,
        output_schema=NotificationResult,
        func=send_sms_notification
    )
    
    # Create workflow
    user_onboarding = Workflow(
        name="User Onboarding",
        description="Onboards a new user and sends welcome notifications",
        input_schema=UserInput
    )
    
    # Define workflow execution pattern
    user_onboarding.then(process_step).then(enrich_step).parallel([email_step, sms_step])
    
    # Execute workflow with streaming updates
    input_data = UserInput(name="Jane Smith", age=28)
    
    print("\n=== Running workflow with StepContext for data sharing ===\n")
    
    async for event in user_onboarding.run_streamed(input_data):
        await handle_workflow_event(event)


if __name__ == "__main__":
    asyncio.run(main()) 