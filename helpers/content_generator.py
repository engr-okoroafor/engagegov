from dotenv import load_dotenv
from openai import OpenAI
from textwrap import dedent
import os


load_dotenv()


# Configure the OpenAI client for xAI's Grok API
api_key = os.getenv("XAI_API_KEY")
client = OpenAI(
   api_key=api_key,
   base_url="https://api.x.ai/v1",
)


def generate_content(prompt: str, tone="professional", temperature=0.7, max_tokens=500) -> str:
   """
   Generate dynamic content using the xAI Grok API.


   Parameters:
       prompt (str): The input text to guide the content generation.
       model (str): The Grok model to use (default: "grok-beta").
       tone (str): Desired tone (e.g., "professional", "casual", "persuasive").
       temperature (float): Creativity level (0.0 to 1.0).
       max_tokens (int): Maximum length of the generated text.


   Returns:
       str: Generated content.
   """
   formatted_prompt = dedent(f""" \
       Based on the promt below generate dynamic content, let it be in the tone specified
       and optimize the content for SEO using the keywords if specified.
       Prompt: {prompt}
       Tone: {tone}


       """)

   try:
       response = client.chat.completions.create(
           model="grok-beta",
           messages=[
               {"role": "system", "content": "You are an experienced content writer."},
               {"role": "user", "content": formatted_prompt},
           ],
           temperature=temperature,
           max_tokens=max_tokens,
           n=1
       )
       return response.choices[0].message.content.strip()
   except Exception as e:
       return f"Error: {e}"
