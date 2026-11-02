
import streamlit as st
import requests

API_URL = "http://localhost:8000/process"

st.set_page_config(
    page_title="Intelligent Document Processing",
    page_icon="📄",
    layout="wide"
)

st.title("📄 Intelligent Document Processing")
st.caption("Upload expense documents for automated extraction and validation.")

st.divider()

uploaded_file = st.file_uploader(
    "Upload your expense document",
    type=["pdf", "png", "jpg", "jpeg"],
    accept_multiple_files=False
)

if uploaded_file:
    st.success(f"Selected: {uploaded_file.name}")

    if st.button("Process Document", type="primary"):
        with st.spinner("Processing document..."):

            try:
                files = {
                    "file": (
                        uploaded_file.name,
                        uploaded_file.getvalue(),
                        uploaded_file.type
                    )
                }

                response = requests.post(
                    API_URL,
                    files=files,
                    timeout=300
                )

                response.raise_for_status()
                result = response.json()

                st.divider()
                st.subheader("Processing Results")

                col1, col2 = st.columns(2)

                with col1:
                    st.metric(
                        "Processing Status",
                        result["status"].upper()
                    )

                with col2:
                    if result["humanreview"]:
                        st.warning("Human Review Required")
                    else:
                        st.success("Validation Passed")

                st.subheader("Extracted Document Data")
                st.json(result["data"])

                st.subheader("Business Validation")

                validation = result["validation"]

                if validation["is_valid"]:
                    st.success("All business validations passed.")
                else:
                    st.error("Financial validation failed.")

                    for error in validation["errors"]:
                        st.warning(error)

            except requests.exceptions.RequestException as error:
                st.error(f"API request failed: {error}")

            except Exception as error:
                st.error(f"Unexpected error: {error}")
