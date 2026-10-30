
import streamlit as st
from pypdf import PdfReader
from PIL import Image
from io import BytesIO
import re


def extract_cbc_values(text):
    """
    Extract CBC values from matching report lines.
    This is experimental text extraction, not clinical interpretation.
    """

    results = {
        "Platelet count": None,
        "Haemoglobin": None,
        "WBC count": None
    }

    for line in text.splitlines():

        clean_line = re.sub(r"\s+", " ", line).strip()
        lower_line = clean_line.lower()

        # Platelet count
        if results["Platelet count"] is None:

            if re.search(r"\bplatelets?\b", lower_line):

                match = re.search(
                    r"\bplatelets?\b.*?\s([0-9,]+(?:\.\d+)?)",
                    clean_line,
                    re.IGNORECASE
                )

                if match:
                    results["Platelet count"] = match.group(1)

        # Haemoglobin
        if results["Haemoglobin"] is None:

            if re.search(
                r"\b(?:haemoglobin|hemoglobin)\b",
                lower_line
            ):

                match = re.search(
                    r"\b(?:haemoglobin|hemoglobin)\b"
                    r"(?:\s*\([^)]*\))?\s+"
                    r"([0-9]+(?:\.\d+)?)",
                    clean_line,
                    re.IGNORECASE
                )

                if match:
                    results["Haemoglobin"] = match.group(1)

        # WBC count
        if results["WBC count"] is None:

            if re.search(
                r"\b(?:wbc|white blood cells?)\b",
                lower_line
            ):

                match = re.search(
                    r"\b(?:wbc|white blood cells?)\b"
                    r"(?:\s*\([^)]*\))?\s+"
                    r"([0-9,]+(?:\.\d+)?)",
                    clean_line,
                    re.IGNORECASE
                )

                if match:
                    results["WBC count"] = match.group(1)

    return results


def show_cbc_report():

    st.header("🩸 CBC Blood Report")

    st.info(
        "Upload a CBC report to extract text and identify common CBC values. "
        "This tool does not diagnose dengue or interpret results clinically."
    )

    extracted_text = ""

    uploaded_file = st.file_uploader(
        "Upload CBC report (PDF or image)",
        type=["pdf", "png", "jpg", "jpeg"],
        key="cbc_upload"
    )

    # PDF upload and text extraction
    if uploaded_file is not None:

        if uploaded_file.type == "application/pdf":

            try:

                reader = PdfReader(
                    BytesIO(uploaded_file.getvalue())
                )

                pages_text = []

                for page_number, page in enumerate(
                    reader.pages,
                    start=1
                ):

                    page_text = page.extract_text() or ""

                    pages_text.append(
                        f"--- Page {page_number} ---\n{page_text}"
                    )

                extracted_text = "\n\n".join(pages_text)

                if extracted_text.strip():

                    st.subheader("📄 Extracted Report Text")

                    st.text_area(
                        "Report content",
                        extracted_text,
                        height=300
                    )

                else:

                    st.warning(
                        "No selectable text found. "
                        "This may be a scanned PDF. "
                        "Please enter values manually."
                    )

            except Exception as error:

                st.error(
                    f"Could not read this PDF: {error}"
                )

        # Image upload
        else:

            try:

                image = Image.open(
                    BytesIO(uploaded_file.getvalue())
                )

                st.image(
                    image,
                    caption="Uploaded CBC report",
                    use_container_width=True
                )

                st.warning(
                    "Image uploaded successfully. "
                    "Automatic image OCR is not enabled yet. "
                    "Please enter values manually."
                )

            except Exception as error:

                st.error(
                    f"Could not open this image: {error}"
                )

    # Automatic CBC extraction
    if extracted_text.strip():

        st.divider()

        st.subheader(
            "🤖 Automatically Detected CBC Values"
        )

        values = extract_cbc_values(extracted_text)

        for name, value in values.items():

            if value is not None:

                st.success(
                    f"{name}: {value}"
                )

            else:

                st.warning(
                    f"{name}: Not detected in this report"
                )

        st.caption(
            "Extracted values must be checked against the original report. "
            "The software does not verify units or clinical correctness."
        )

    # Manual CBC values
    st.divider()

    st.subheader(
        "Enter CBC Values Manually (Optional)"
    )

    platelet = st.number_input(
        "Platelet count (/µL)",
        min_value=0,
        max_value=2000000,
        value=0,
        step=100
    )

    haemoglobin = st.number_input(
        "Haemoglobin (g/dL)",
        min_value=0.0,
        max_value=30.0,
        value=0.0,
        step=0.1
    )

    wbc = st.number_input(
        "WBC count (/µL)",
        min_value=0,
        max_value=200000,
        value=0,
        step=100
    )

    if st.button("Show Entered Values"):

        st.subheader("Values Entered")

        st.write(
            f"Platelet count: "
            f"{platelet if platelet else 'Not entered'}"
        )

        st.write(
            f"Haemoglobin: "
            f"{haemoglobin if haemoglobin else 'Not entered'}"
        )

        st.write(
            f"WBC count: "
            f"{wbc if wbc else 'Not entered'}"
        )

        st.caption(
            "These are user-entered values, not a diagnosis. "
            "Please have the complete report reviewed by a qualified clinician."
        )

    st.divider()

    st.warning(
        "CBC values alone cannot confirm or rule out dengue. "
        "Consult a qualified healthcare professional for medical assessment."
    )
 