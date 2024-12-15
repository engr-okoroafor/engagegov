import time
import streamlit as st
from helpers.image_utils import encode_image_to_base64
from helpers.api_utils import extract_text_from_image, summarize_text, generate_insights
from helpers.content_generator import generate_content  # Importing the content generation function

# Function to check network status with a delay
def check_network_status():
    network_status = st.components.v1.html(
        """
        <script>
            function checkNetworkStatus() {
                if (!navigator.onLine) {
                    setTimeout(function() {
                        window.parent.postMessage({isOffline: true}, "*");
                    }, 3000);  // 3 seconds delay before notifying the parent component
                }
            }
            checkNetworkStatus();
        </script>
        """, height=0, width=0
    )
    return network_status

# Initialize session state variables
if "extracted_text" not in st.session_state:
    st.session_state.extracted_text = ""
if "summary" not in st.session_state:
    st.session_state.summary = ""
if "insights" not in st.session_state:
    st.session_state.insights = ""
if "current_ministry" not in st.session_state:
    st.session_state.current_ministry = "General"

# Define ministries (hidden temporarily)
ministries = [
    "Health", "Agriculture", "Education", "Technology", "Infrastructure", "Transport", "Lands", "Immigration", "Military",
]

# Main dashboard
st.title("Citizen Engagement and Reporting Platform")
st.sidebar.header("🌐Ministry Navigation")
st.sidebar.write("Currently, only the General Reporting Channel is available.")

# Sidebar for ministry navigation (only General visible)
selected_ministry = st.sidebar.radio(
    "Select Ministry", options=["General"]
)
st.session_state.current_ministry = selected_ministry

st.header("📢General Reporting")

# File uploader for image inputs
uploaded_file = st.file_uploader("Upload a photo report (optional)", type=["png", "jpg", "jpeg"])

# Check file validity
if uploaded_file:
    file_size = uploaded_file.size / (1024 * 1024)  # File size in MB
    if file_size > 200:
        st.error("❌File size exceeds 200MB. Please upload a smaller file.")
    else:
        # Display uploaded image
        st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)

        # Save image temporarily
        with open("temp_image.jpg", "wb") as f:
            f.write(uploaded_file.read())

        try:
            # Create placeholders for progress messages
            encoding_placeholder = st.empty()
            extracting_placeholder = st.empty()
            summarizing_placeholder = st.empty()
            insights_placeholder = st.empty()

            # Encode image to Base64
            encoding_placeholder.info("Encoding image...")
            image_base64 = encode_image_to_base64("temp_image.jpg")
            encoding_placeholder.success("Image encoded successfully!")

            # Extract text from the image
            extracting_placeholder.info("Extracting text from the image...")
            st.session_state.extracted_text = extract_text_from_image(image_base64)
            extracting_placeholder.success("Text extracted successfully!")

            # Summarize the extracted text automatically
            if st.session_state.extracted_text:
                summarizing_placeholder.info("Summarizing text...")
                st.session_state.summary = summarize_text(st.session_state.extracted_text)
                summarizing_placeholder.success("Text summarized successfully!")

            # Generate actionable insights automatically
            if st.session_state.summary:
                insights_placeholder.info("Generating actionable insights...")
                st.session_state.insights = generate_insights(st.session_state.summary)
                insights_placeholder.success("Insights generated successfully!")

            # After all processing is done, clear placeholders
            encoding_placeholder.empty()
            extracting_placeholder.empty()
            summarizing_placeholder.empty()
            insights_placeholder.empty()

        except Exception as e:
            # Handle error if the issue is not related to file format
            if isinstance(e, FileNotFoundError):
                # Check network status after 3 seconds
                network_status = check_network_status()
                # Here, we will need a mechanism to capture the offline message from JS
                if network_status == 'offline':
                    st.error("Network connection error. Please check your internet connection and try again.")
                    st.warning("Reconnecting...")
                    st.experimental_rerun()
            else:
                st.error(f"❌An error occurred: {e}")
                st.warning("Please upload a valid image file (PNG, JPG, JPEG) and ensure it's under 200MB.")

# Display the extracted text
if st.session_state.extracted_text:
    st.subheader("📄Extracted Text:")
    st.text_area("Extracted Text", st.session_state.extracted_text, height=200)

# Display the summary
if st.session_state.summary:
    st.subheader("📝Summary:")
    st.text_area("Summary", st.session_state.summary, height=150)

# Display the insights
if st.session_state.insights:
    st.subheader("💡Actionable Insights:")
    st.text_area("Insights", st.session_state.insights, height=150)

# Text input for reporting or inquiries
user_query = st.text_area("✍️...Describe your report.")

# Handle submissions
if st.button("🚀Submit"):
    if not user_query.strip() and not uploaded_file:
        st.error("Please provide text input or upload a photo.")
    else:
        st.info("Processing your request...")

        # Use Grok AI to analyze and route the query
        response = generate_insights(user_query)  # Replace with actual Grok API call for routing
        if selected_ministry == "General":
            st.success("AI suggests routing to the appropriate ministry...")
            # Example logic to determine ministry based on AI response
            suggested_ministry = "Health"  # Replace with response['ministry'] from Grok API
            st.write(f"This query is related to: **{suggested_ministry}**")
        else:
            st.success("Query processed successfully by the selected ministry!")

        # Display AI-generated suggestions
        suggestions = summarize_text(user_query)  # Replace with Grok API for tailored advice
        st.subheader("Suggestions and Insights")
        st.text_area("Tailored Suggestions", suggestions, height=150)

# General content generation
st.subheader("Ask the Government")
prompt = st.text_area("✍️...Enter a topic for personalized advice.", "")
if st.button("🚀Generate Response"):
    if not prompt.strip():
        st.error("Please provide a topic.")
    else:
        with st.spinner("Generating content..."):
            content = generate_content(prompt, tone="Professional", temperature=0.7, max_tokens=1500)
        if content:
            st.success("✅Content generated successfully!")
            st.markdown(content, unsafe_allow_html=True)
        else:
            st.error("❌Failed to generate content. Please try again.")
            

