from pydantic import BaseModel
import asyncio


import sys
import os

# Add the project root directory to Python's path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from v2.workflow.workflow import Workflow
from v2.step.step import Step
from v2.workflow.runner import Runner

# Define input and output schemas
class ImageData(BaseModel):
    image_path: str
    metadata: dict

class ResizedImage(BaseModel):
    width: int
    height: int
    image_data: bytes

class DetectionResult(BaseModel):
    objects: list
    confidence_scores: list

class FilteredResult(BaseModel):
    detected_objects: list
    object_count: int


# Define step functions
async def resize_image(data: ImageData) -> ResizedImage:
    # In a real implementation, this would actually resize the image
    print(f"Resizing image from {data.image_path}")
    # Simulate resized image data
    return ResizedImage(
        width=800,
        height=600,
        image_data=b"simulated_resized_image_data"
    )

async def detect_objects(data: ImageData) -> DetectionResult:
    # In a real implementation, this would run object detection
    print(f"Detecting objects in {data.image_path}")
    # Simulate detection results
    return DetectionResult(
        objects=["person", "car", "dog"],
        confidence_scores=[0.92, 0.85, 0.78]
    )

async def filter_results(data: dict) -> FilteredResult:
    # This step takes the combined results from parallel steps
    detection_results = data.get("Detect Objects")

    print(data)
    # Filter objects with confidence > 0.8
    filtered_objects = [
        obj for obj, score in zip(
            detection_results.objects, 
            detection_results.confidence_scores
        ) if score > 0.8
    ]
    
    return FilteredResult(
        detected_objects=filtered_objects,
        object_count=len(filtered_objects)
    )


# Create steps
resize_step = Step(
    name="Resize Image",
    func=resize_image,
    input_schema=ImageData,
    output_schema=ResizedImage
)

detect_step = Step(
    name="Detect Objects",
    func=detect_objects,
    input_schema=ImageData,
    output_schema=DetectionResult
)

filter_step = Step(
    name="Filter Results",
    func=filter_results,
    input_schema=dict,  # The output of parallel steps is a dict
    output_schema=FilteredResult
)


# Define the workflow
image_processing_workflow = Workflow(
    name="Image Processing",
    input_schema=ImageData,
    description="A workflow that processes images in parallel"
)

# Add parallel steps to the workflow followed by a step that uses their combined results
image_processing_workflow.parallel([resize_step, detect_step]).then(filter_step)


# Run the workflow
async def main():
    # Initialize the runner
    runner = Runner(workflow=image_processing_workflow)
    
    # Prepare input data
    input_data = ImageData(
        image_path="/path/to/example.jpg",
        metadata={"created_at": "2023-05-15", "author": "user123"}
    )
    
    # Run the workflow
    result = await runner.run(input_data)
    
    # Display the result
    print(f"\nDetected objects (confidence > 0.8): {result.detected_objects}")
    print(f"Number of high-confidence objects: {result.object_count}")


if __name__ == "__main__":
    asyncio.run(main()) 