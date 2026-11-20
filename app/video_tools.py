"""Video generation tool using gemini-omni-flash-preview in global region."""

import base64
import time
import uuid
from google import genai
from google.genai import types
from google.cloud import storage
from google.adk.tools import ToolContext

GCP_PROJECT_ID = "qwiklabs-gcp-03-144fb6d3227f"
GCS_BUCKET_NAME = "greenhouse-assistant-media-qwiklabs-gcp-03-144fb6d3227f"


async def generate_plant_video(scene_description: str, tool_context: ToolContext) -> str:
    """Generates a short realistic video for a greenhouse plant or botanical scene
    using Google's Omni model (gemini-omni-flash-preview) in the global region.

    Saves the video as a session artifact in the Playground, and uploads it to the public
    Cloud Storage bucket, returning the permanent public https URL.

    Args:
        scene_description: A description of the plant scene or botanical time-lapse to generate
            (e.g., 'A vibrant Monstera Deliciosa with dew drops glistening on its leaves in a sunlit greenhouse').
        tool_context: ADK tool context used to save the artifact for the session.

    Returns:
        The public HTTPS URL of the uploaded video on Google Cloud Storage.
    """
    try:
        client = genai.Client(vertexai=True, project=GCP_PROJECT_ID, location="global")
        prompt = (
            f"A realistic, high quality, cinematic video clip of {scene_description}, "
            "vibrant natural greenhouse atmosphere, smooth camera motion."
        )

        interaction = client.interactions.create(
            model="gemini-omni-flash-preview",
            input=prompt,
        )

        video_bytes = None
        if hasattr(interaction, "output_video") and interaction.output_video and interaction.output_video.data:
            video_bytes = base64.b64decode(interaction.output_video.data)
        elif hasattr(interaction, "outputs") and interaction.outputs:
            for out in interaction.outputs:
                if getattr(out, "type", None) == "video" and getattr(out, "data", None):
                    video_bytes = base64.b64decode(out.data)
                    break

        if not video_bytes:
            return "Error: Omni model did not return video data."

        mime_type = "video/mp4"
        filename = f"plant_video_{int(time.time())}_{uuid.uuid4().hex[:6]}.mp4"

        # 1. Save as artifact for Playground Artifacts panel
        artifact_part = types.Part.from_bytes(data=video_bytes, mime_type=mime_type)
        if tool_context:
            await tool_context.save_artifact(filename=filename, artifact=artifact_part)

        # 2. Upload to public Cloud Storage bucket
        storage_client = storage.Client(project=GCP_PROJECT_ID)
        bucket = storage_client.bucket(GCS_BUCKET_NAME)
        blob = bucket.blob(filename)
        blob.upload_from_string(video_bytes, content_type=mime_type)

        public_url = f"https://storage.googleapis.com/{GCS_BUCKET_NAME}/{filename}"
        return public_url
    except Exception as e:
        return f"Error generating or saving video: {str(e)}"
