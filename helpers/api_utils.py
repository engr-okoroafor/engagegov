from dotenv import load_dotenv
from openai import OpenAI
import os

# Load environment variables from .env file
load_dotenv()

# Load both API keys from the .env file
grok_api_key = os.getenv("XAI_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")

# Configure the OpenAI client for xAI's Grok API
api_key = os.getenv("XAI_API_KEY")
client = OpenAI(
    api_key=api_key,
    base_url="https://api.x.ai/v1",
)

def extract_text_from_image(image_base64: str) -> str:
    """
    Extract text from an image using Grok Vision API.

    Args:
        image_base64 (str): Base64 encoded image string.

    Returns:
        str: Extracted text from the image.
    """
    response = client.chat.completions.create(
        model="grok-vision-beta",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Extract and give me the text in the image provided, and nothing else no intro"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}"
                        }
                    }
                ]
            }
        ],
        temperature=0.7,
        max_tokens=1000,
        n=1
    )
    return response.choices[0].message.content.strip()

def summarize_text(text: str) -> str:
    """
    Summarize extracted text using Grok API.

    Args:
        text (str): Extracted text.

    Returns:
        str: Summary of the text.
    """
    response = client.chat.completions.create(
        model="grok-beta",
        messages=[
            {
                "role": "user",
                "content": f"Summarize the following text:\n\n{text}"
            }
        ],
        temperature=0.7,
        max_tokens=500,
        n=1
    )
    return response.choices[0].message.content.strip()

def generate_insights(summary: str) -> str:
    """
    Generate actionable insights from a summary using Grok API.

    Args:
        summary (str): Summary of the text.

    Returns:
        str: Actionable insights derived from the summary.
    """
    response = client.chat.completions.create(
        model="grok-beta",
        messages=[
            {
                "role": "user",
                "content": f"Based on the following summary, generate actionable insights:\n\n{summary}"
            }
        ],
        temperature=0.7,
        max_tokens=500,
        n=1
    )
    return response.choices[0].message.content.strip()