import streamlit as st
import os
import requests
from dotenv import load_dotenv
from typing import Optional
from requests.exceptions import RequestException, ConnectionError
from helpers.image_utils import encode_image_to_base64
from helpers.api_utils import extract_text_from_image, summarize_text, generate_insights

# Load environment variables
load_dotenv()

# Constants
BASE_API_URL = "https://api.langflow.astra.datastax.com"
LANGFLOW_ID = "a76d6046-9bc2-4704-b2d5-67d042b61b8d"
FLOW_ID = "f9bf7aa5-05a2-432e-ae2f-2bb4dfd0fc4a"
APPLICATION_TOKEN = os.getenv("APP_TOKEN")
ENDPOINT = "engagegov"

# Initialize session state variables
if "response" not in st.session_state:
    st.session_state.response = ""
if "extracted_text" not in st.session_state:
    st.session_state.extracted_text = ""
if "summary" not in st.session_state:
    st.session_state.summary = ""
if "insights" not in st.session_state:
    st.session_state.insights = ""

# Function to run the flow
def run_flow(
    message: str,
    endpoint: str,
    output_type: str = "chat",
    input_type: str = "chat",
    tweaks: Optional[dict] = None,
    application_token: Optional[str] = None,
) -> dict:
    api_url = f"{BASE_API_URL}/lf/{LANGFLOW_ID}/api/v1/run/{endpoint}"
    payload = {"input_value": message, "output_type": output_type, "input_type": input_type}
    headers = {"Authorization": f"Bearer {application_token}", "Content-Type": "application/json"}

    try:
        response = requests.post(api_url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except ConnectionError:
        st.error("Network error: Unable to reach the API. Please check your internet connection or try again later.")
        return None
    except RequestException as e:
        st.error(f"An error occurred while contacting the API: {e}")
        return None
    except ValueError as e:
        st.error(f"Failed to decode JSON from the response: {e}")
        return None

# Streamlit Interface
st.set_page_config(page_title="Citizen Engagement and Reporting Platform", layout="wide")
st.title("Citizen Engagement and Reporting Platform")

# Image Analysis Section
st.header("📷 Image Analysis")
uploaded_file = st.file_uploader("Upload a photo report (optional)", type=["png", "jpg", "jpeg"])

if uploaded_file:
    file_size = uploaded_file.size / (1024 * 1024)  # File size in MB
    if file_size > 200:
        st.error("❌ File size exceeds 200MB. Please upload a smaller file.")
    else:
        st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
        with open("temp_image.jpg", "wb") as f:
            f.write(uploaded_file.read())

        try:
            # Placeholders for step-by-step processing
            processing_placeholder = st.empty()
            
            processing_placeholder.info("Encoding image...")
            image_base64 = encode_image_to_base64("temp_image.jpg")
            processing_placeholder.info("Image encoded successfully!")

            processing_placeholder.info("Extracting text from the image...")
            st.session_state.extracted_text = extract_text_from_image(image_base64)
            processing_placeholder.info("Text extracted successfully!")

            if st.session_state.extracted_text:
                processing_placeholder.info("Summarizing text...")
                st.session_state.summary = summarize_text(st.session_state.extracted_text)
                processing_placeholder.info("Text summarized successfully!")

            if st.session_state.summary:
                processing_placeholder.info("Generating actionable insights...")
                st.session_state.insights = generate_insights(st.session_state.summary)
                # Replace all messages with a final success message
                processing_placeholder.success("✅ Content generated successfully!")

        except Exception as e:
            st.error(f"❌ An error occurred: {e}")
            st.warning("Please upload a valid image file (PNG, JPG, JPEG) and ensure it's under 200MB.")


# Display Image Analysis Results
if st.session_state.extracted_text:
    st.subheader("📄 Extracted Text:")
    st.text_area("Extracted Text", st.session_state.extracted_text, height=200)

if st.session_state.summary:
    st.subheader("📝 Summary:")
    st.text_area("Summary", st.session_state.summary, height=150)

if st.session_state.insights:
    st.subheader("💡 Actionable Insights:")
    st.text_area("Insights", st.session_state.insights, height=150)

# General Reporting Section
st.header("📢 General Reporting/Inquiry")
query = st.text_area("✍️ Describe your report or inquiry:", placeholder="What is the ministry in charge of fixing roads?", height=150)

# Submit Query
if st.button("Submit 🚀"):
    if query.strip() == "" and not uploaded_file:
        st.error("Please provide text input or upload a photo.")
    else:
        try:
            with st.spinner("Loading... Please wait."):
                response = run_flow(message=query, endpoint=ENDPOINT, application_token=APPLICATION_TOKEN)

                if response:
                    outputs = response.get("outputs", [])
                    formatted_response = "\n\n".join(
                        f"- {output.get('results', {}).get('message', {}).get('text', '')}" for item in outputs for output in item.get("outputs", [])
                    )
                    st.session_state.response = formatted_response or "No relevant outputs received from the API."
                else:
                    st.session_state.response = "No valid response received from the API."

                st.success("✅ Content generated successfully!")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")

# Display AI Response
if st.session_state.response:
    st.subheader("💬 AI Response:")
    st.markdown(st.session_state.response, unsafe_allow_html=True)

# Footer
st.markdown("**Developed with ❤️ by [Chukwudifu Uzoma Okoroafor, engr.okoroafor@gmail.com]**")
