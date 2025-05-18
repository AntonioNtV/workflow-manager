import asyncio
from typing import Dict
from pydantic import BaseModel

from workflow import (
    Step, Workflow, Runner
)

# Define input and output models
class UserData(BaseModel):
    name: str
    age: int
    location: str

class NameOutput(BaseModel):
    formatted_name: str

class AgeOutput(BaseModel):
    age_category: str
    years_to_100: int

class LocationOutput(BaseModel):
    country: str
    is_northern: bool

class FinalOutput(BaseModel):
    name_info: str
    age_info: str
    location_info: str

# Define step functions
async def process_name(input_data: UserData) -> NameOutput:
    """Process the user's name."""
    await asyncio.sleep(1)  # Simulate processing time
    name_parts = input_data.name.split()
    formatted = f"{name_parts[-1].upper()}, {name_parts[0]}"
    return NameOutput(formatted_name=formatted)

async def process_age(input_data: UserData) -> AgeOutput:
    """Process the user's age."""
    await asyncio.sleep(2)  # Simulate processing time
    
    category = "child" if input_data.age < 18 else (
        "senior" if input_data.age >= 65 else "adult"
    )
    
    years_to_100 = 100 - input_data.age
    
    return AgeOutput(
        age_category=category,
        years_to_100=years_to_100
    )

async def process_location(input_data: UserData) -> LocationOutput:
    """Process the user's location."""
    await asyncio.sleep(1.5)  # Simulate processing time
    
    # Simplified logic for example
    northern_countries = ["Canada", "Norway", "Sweden", "Finland", "Russia"]
    is_northern = input_data.location in northern_countries
    
    return LocationOutput(
        country=input_data.location,
        is_northern=is_northern
    )

async def combine_results(input_data: Dict[str, any]) -> FinalOutput:
    """Combine results from parallel steps."""
    # The input will be a dictionary with step IDs as keys
    name_result = input_data["process_name"]
    age_result = input_data["process_age"]
    location_result = input_data["process_location"]
    
    name_info = f"Name: {name_result.formatted_name}"
    
    age_info = (
        f"Age Category: {age_result.age_category}, "
        f"Years to 100: {age_result.years_to_100}"
    )
    
    location_info = (
        f"Location: {location_result.country}, "
        f"{'Northern' if location_result.is_northern else 'Not Northern'} region"
    )
    
    return FinalOutput(
        name_info=name_info,
        age_info=age_info,
        location_info=location_info
    )

# Create workflow steps
name_step = Step(
    id="process_name",
    name="Process Name",
    description="Processes the user's name",
    input_schema=UserData,
    output_schema=NameOutput,
    func=process_name
)

age_step = Step(
    id="process_age",
    name="Process Age",
    description="Processes the user's age",
    input_schema=UserData,
    output_schema=AgeOutput,
    func=process_age
)

location_step = Step(
    id="process_location",
    name="Process Location",
    description="Processes the user's location",
    input_schema=UserData,
    output_schema=LocationOutput,
    func=process_location
)

combine_step = Step(
    id="combine_results",
    name="Combine Results",
    description="Combines the results from parallel processing",
    input_schema=dict,  # Using dict as the schema for simplicity
    output_schema=FinalOutput,
    func=combine_results
)

# Create the workflow
workflow = Workflow(
    name="Parallel Processing Workflow",
    description="A workflow that processes user data in parallel",
    input_schema=UserData
)

# Add steps to the workflow - parallel processing followed by combination
workflow.parallel([name_step, age_step, location_step]).then(combine_step)

# Run the workflow
async def main():
    # Create a runner
    runner = Runner(workflow)
    
    # Input data
    user_data = UserData(
        name="John Doe",
        age=35,
        location="Canada"
    )
    
    print(f"Processing data for user: {user_data}")
    print("Running parallel workflow...")
    
    # Run the workflow and time it
    start_time = asyncio.get_event_loop().time()
    result = await runner.run(user_data)
    end_time = asyncio.get_event_loop().time()
    
    # Print the results
    print(f"\nWorkflow completed in {end_time - start_time:.2f} seconds")
    print("\nResults:")
    print(f"  {result.name_info}")
    print(f"  {result.age_info}")
    print(f"  {result.location_info}")
    
    # Note: In a real parallel implementation, the total time would be closer to 
    # the longest individual step (2 seconds) rather than the sum (4.5 seconds)

if __name__ == "__main__":
    asyncio.run(main()) 