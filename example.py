import asyncio
from typing import Dict, List, Any
from pydantic import BaseModel

from workflow import Step, Workflow


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


# Define step functions
async def process_user_data(user_input: UserInput):
    """Process initial user data and create a user profile."""
    
    # Create a user ID and basic profile
    user_id = f"user_{user_input.name.lower().replace(' ', '_')}_{user_input.age}"
    profile = {
        "name": user_input.name,
        "age": user_input.age,
        "created_at": "2023-05-20T14:30:00Z"  # In a real app, use current timestamp
    }
    
    # Simulate processing delay
    await asyncio.sleep(0.5)
    
    return ProcessedUserData(user_id=user_id, profile=profile)


async def enrich_user_data(processed_data: ProcessedUserData):
    """Enrich user data with additional information."""
    # Add preferences based on user age
    if processed_data.profile["age"] < 18:
        preferences = ["games", "music", "education"]
    elif processed_data.profile["age"] < 30:
        preferences = ["travel", "tech", "sports"]
    else:
        preferences = ["news", "cooking", "health"]
    
    # Simulate processing delay
    await asyncio.sleep(0.5)
    
    return EnrichedUserData(
        user_id=processed_data.user_id,
        profile=processed_data.profile,
        preferences=preferences
    )


async def send_email_notification(user_data: EnrichedUserData):
    """Send email notification to the user."""
    # Simulate sending an email
    print(f"Sending email to user {user_data.user_id}")
    await asyncio.sleep(0.2)
    
    return NotificationResult(
        user_id=user_data.user_id,
        notification_sent=True,
        channel="email"
    )


async def send_sms_notification(user_data: EnrichedUserData):
    """Send SMS notification to the user."""
    # Simulate sending an SMS
    print(f"Sending SMS to user {user_data.user_id}")
    await asyncio.sleep(0.2)
    
    return NotificationResult(
        user_id=user_data.user_id,
        notification_sent=True,
        channel="sms"
    )


async def main():
    # Create steps
    process_step = Step(
        name="Process User Data",
        description="Processes raw user input and creates a user profile",
        input_schema=UserInput,
        output_schema=ProcessedUserData,
        func=process_user_data,
    )
    
    enrich_step = Step(
        name="Enrich User Data",
        description="Enriches user data with additional information",
        input_schema=ProcessedUserData,
        output_schema=EnrichedUserData,
        func=enrich_user_data
    )
    
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
    
    # Create a workflow
    user_onboarding = Workflow(
        name="User Onboarding",
        description="Onboards a new user and sends welcome notifications",
        input_schema=UserInput
    )
    
    # Define the workflow execution pattern
    user_onboarding.then(process_step).then(enrich_step).parallel([email_step, sms_step])
    
    # Execute the workflow
    input_data = UserInput(name="John Doe", age=25)
    result = await user_onboarding.execute(input_data)


if __name__ == "__main__":
    asyncio.run(main()) 