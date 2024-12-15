import streamlit as st
from helpers.api_utils import generate_insights, summarize_text

def display_page():
    st.title("Immigration Ministry")
    st.subheader("Report or Make an Inquiry")
    
    uploaded_file = st.file_uploader("Upload an image (optional)", type=["png", "jpg", "jpeg"])
    text_input = st.text_area("Describe your health-related issue or inquiry")

    if st.button("Submit"):
        st.info("Processing your report...")
        # AI Logic
        summary = summarize_text(text_input)
        insights = generate_insights(summary)
        st.success("Your inquiry has been processed!")
        st.write(f"AI Suggestions: {insights}")
