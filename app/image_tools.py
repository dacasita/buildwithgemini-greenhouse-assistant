"""Image generation tool using gemini-3.1-flash-lite-image in global region."""

import time
import uuid
from google import genai
from google.genai import types
from google.cloud import storage
from google.adk.tools import ToolContext

# Hardcoded project and bucket name per lab instructions:
GCP_PROJECT_ID = "qwiklabs-gcp-03-144fb6d3227f"
GCS_BUCKET_NAME = "greenhouse-assistant-media-qwiklabs-gcp-03-144fb6d3227f"


async def generate_plant_image(plant_description: str, tool_context: ToolContext) -> str:
    """Generates a high-quality visual image for a greenhouse plant or botanical scene
    using gemini-3.1-flash-lite-image in the global region.

    Saves the image as a session artifact in the Playground, and uploads it to the public
    Cloud Storage bucket, returning the permanent public https URL.

    Args:
        plant_description: A description of the plant or arrangement to generate (e.g.
            'A thriving Monstera Deliciosa in a terracotta pot with soft sunlight').
        tool_context: ADK tool context used to save the artifact for the session.

    Returns:
        The public HTTPS URL of the uploaded image on Google Cloud Storage.
    """
    try:
        client = genai.Client(vertexai=True, project=GCP_PROJECT_ID, location="global")
        prompt = (
            f"A beautiful, high quality, realistic botanical photograph of {plant_description}, "
            "vibrant natural green foliage, well lit, elegant indoor planter"
        )
        response = client.models.generate_content(
            model="gemini-3.1-flash-lite-image",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
            ),
        )

        image_bytes = None
        mime_type = "image/jpeg"
        if response.candidates and response.candidates[0].content:
            for part in response.candidates[0].content.parts:
                if part.inline_data and part.inline_data.data:
                    image_bytes = part.inline_data.data
                    mime_type = part.inline_data.mime_type or "image/jpeg"
                    break

        if not image_bytes:
            return "Error: Model did not return image data."

        ext = "jpg" if "jpeg" in mime_type else "png"
        filename = f"plant_{int(time.time())}_{uuid.uuid4().hex[:6]}.{ext}"

        # 1. Save as artifact for Playground Artifacts panel
        artifact_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
        if tool_context:
            await tool_context.save_artifact(filename=filename, artifact=artifact_part)


        # 2. Upload to public Cloud Storage bucket
        storage_client = storage.Client(project=GCP_PROJECT_ID)
        bucket = storage_client.bucket(GCS_BUCKET_NAME)
        blob = bucket.blob(filename)
        blob.upload_from_string(image_bytes, content_type=mime_type)

        public_url = f"https://storage.googleapis.com/{GCS_BUCKET_NAME}/{filename}"
        return public_url
    except Exception as e:
        return f"Error generating or saving image: {str(e)}"
