import streamlit as st
import os
import requests
import time
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
state_keys = ["response_history", "extracted_text", "summary", "insights"]
for key in state_keys:
    if key not in st.session_state:
        st.session_state[key] = [] if key == "response_history" else ""

# Utility function for API calls with retry and rate limiting
def run_flow_with_backoff(message: str, endpoint: str, application_token: Optional[str], retries=5) -> dict:
    api_url = f"{BASE_API_URL}/lf/{LANGFLOW_ID}/api/v1/run/{endpoint}"
    payload = {"input_value": message, "output_type": "chat", "input_type": "chat"}
    headers = {
        "Authorization": f"Bearer {application_token}",
        "Content-Type": "application/json",
    }

    for attempt in range(retries):
        try:
            response = requests.post(api_url, json=payload, headers=headers)
            if response.status_code == 429:  # Handle rate limit
                retry_after = int(response.headers.get("Retry-After", 1))
                time.sleep(retry_after)
                continue
            response.raise_for_status()
            return response.json()
        except ConnectionError:
            st.error("Network error: Unable to reach the API. Please check your connection.")
        except RequestException as e:
            if attempt < retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                st.error(f"API error: {e}")
                return None

# Streamlit Configuration
st.set_page_config(
    page_title="Citizen Engagement Platform",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.title("Citizen Engagement and Reporting Platform")

# Image Upload Section
st.header("📷 Upload Image Report")
uploaded_file = st.file_uploader("Upload a photo report (optional)", type=["png", "jpg", "jpeg"])

if uploaded_file:
    file_size = uploaded_file.size / (1024 * 1024)  # File size in MB
    if file_size > 200:
        st.error("❌ File size exceeds 200MB. Please upload a smaller file.")
    else:
        st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)
        try:
            temp_image_path = "temp_image.jpg"
            with open(temp_image_path, "wb") as f:
                f.write(uploaded_file.read())

            processing_placeholder = st.empty()
            processing_placeholder.info("Processing image...")

            image_base64 = encode_image_to_base64(temp_image_path)
            st.session_state.extracted_text = extract_text_from_image(image_base64)

            if st.session_state.extracted_text:
                st.session_state.summary = summarize_text(st.session_state.extracted_text)
                st.session_state.insights = generate_insights(st.session_state.summary)
                processing_placeholder.success("✅ Analysis completed successfully!")
            else:
                processing_placeholder.error("No text extracted from the image.")
        except Exception as e:
            st.error(f"Error processing the image: {e}")

# Display Results for Image Reporting
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
query = st.text_area("✍️ Describe your report or inquiry:", placeholder="What initiatives exist for reducing unemployment?", height=150)

if st.button("Submit 🚀", key="submit_button"):
    if not query.strip():
        st.error("Please provide text input.")
    else:
        try:
            with st.spinner("Processing your request..."):
                response = run_flow_with_backoff(query, ENDPOINT, APPLICATION_TOKEN)
                ai_response = ""
                if response:
                    outputs = response.get("outputs", [])
                    ai_response = (
                        "\n\n".join(
                            f"- {output.get('results', {}).get('message', {}).get('text', '')}"
                            for item in outputs
                            for output in item.get("outputs", [])
                        )
                        or "No outputs received from the API."
                    )
                else:
                    ai_response = "No valid response received."

                st.session_state.response_history.insert(0, {"query": query, "response": ai_response})
        except Exception as e:
            st.error(f"Unexpected error: {e}")

# Display Query-Response History
if st.session_state.response_history:
    st.subheader("🗂️ Query-Response History")
    for i, entry in enumerate(st.session_state.response_history):
        st.markdown("#### 👤 User:")
        st.markdown(
            f"""
            <div style="background-color:rgb(240, 227, 254); padding: 10px; border-radius: 10px; width: fit-content; max-width: 90%; word-wrap: break-word;">
                {entry['query']}
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("#### 💬 AI Response:")
        st.markdown(
            f"""
            <div style="background-color:rgb(223, 250, 229); padding: 10px; border-radius: 10px; width: fit-content; max-width: 90%; word-wrap: break-word;">
                {entry['response'].replace('\n', '<br>')}
            </div>
            """,
            unsafe_allow_html=True,
        )

# Footer
st.markdown(
    "<br><hr><center><b>Developed with ❤️ by Chukwudifu Uzoma Okoroafor</b> | Contact: engr.okoroafor@gmail.com</center><hr>",
    unsafe_allow_html=True,
)
