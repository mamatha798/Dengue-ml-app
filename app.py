import streamlit as st
import sqlite3
import urllib.request
from datetime import datetime
from io import BytesIO
import pandas as pd
import json

# ==================================================
# PAGE CONFIGURATION
# ==================================================
st.set_page_config(
    page_title="Dengue AI Guardian | Health Dashboard",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

DB_NAME = "dengue_guardian.db"

# ==================================================
# PROFESSIONAL HEALTHCARE DESIGN
# ==================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"], [data-testid="stApp"] {
    font-family: 'Inter', sans-serif;
}

[data-testid="stAppViewContainer"] {
    background-color: #F5F8FC;
}

[data-testid="stHeader"] {
    background-color: #F5F8FC;
}

/* Sidebar size and appearance */
[data-testid="stSidebar"] {
    min-width: 285px;
    background-color: #102A43;
}

[data-testid="stSidebar"] > div:first-child {
    background-color: #102A43;
}

[data-testid="stSidebar"] * {
    color: #FFFFFF;
}

[data-testid="stSidebar"] h1 {
    font-size: 25px !important;
    font-weight: 800 !important;
}

[data-testid="stSidebar"] h2 {
    font-size: 21px !important;
    font-weight: 700 !important;
}

[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label {
    font-size: 18px !important;
    line-height: 1.7 !important;
}

/* Navigation radio options */
[data-testid="stSidebar"] [role="radiogroup"] label {
    padding: 8px 6px;
    margin-bottom: 5px;
    font-size: 18px !important;
    font-weight: 500 !important;
}

/* Main headings */
h1 {
    color: #102A43 !important;
    font-size: 32px !important;
    font-weight: 800 !important;
}

h2 {
    color: #163A56 !important;
    font-size: 25px !important;
    font-weight: 700 !important;
}

h3 {
    color: #163A56 !important;
    font-size: 20px !important;
    font-weight: 700 !important;
}

/* General readable text */
.stMarkdown p,
.stMarkdown li {
    font-size: 16px;
    line-height: 1.7;
}

label, .stSelectbox, .stNumberInput, .stRadio {
    font-size: 16px !important;
}

/* Buttons */
.stButton button,
.stFormSubmitButton button {
    min-height: 44px;
    font-size: 17px !important;
    font-weight: 600 !important;
    border-radius: 8px;
}

/* Cards */
div[data-testid="stMetric"] {
    background-color: #FFFFFF;
    padding: 18px;
    border: 1px solid #E1E8F0;
    border-radius: 12px;
}

div[data-testid="stMetricLabel"] {
    font-size: 15px !important;
}

div[data-testid="stMetricValue"] {
    color: #147D92;
    font-weight: 700;
}

hr {
    border-color: #DCE5EE;
}

.small-note {
    color: #526579;
    font-size: 13px;
}

.app-banner {
    background: linear-gradient(110deg, #102A43, #147D92);
    color: white;
    padding: 25px;
    border-radius: 14px;
    margin-bottom: 20px;
}

.app-banner h2 {
    color: white !important;
    margin-bottom: 6px;
}

.app-banner p {
    color: #E5F4F7;
    font-size: 16px;
}
</style>
""", unsafe_allow_html=True)


# ==================================================
# DATABASE
# ==================================================
def init_database():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS patient_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                record_date TEXT NOT NULL,
                fever_temp REAL,
                headache TEXT,
                skin_rash TEXT,
                vomiting TEXT,
                platelet_count INTEGER,
                joint_pain TEXT,
                nausea TEXT,
                travel_history TEXT,
                symptom_score INTEGER
            )
        """)
        conn.commit()


def save_record(data):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
            INSERT INTO patient_records (
                record_date, fever_temp, headache, skin_rash,
                vomiting, platelet_count, joint_pain, nausea,
                travel_history, symptom_score
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            data["fever_temp"],
            data["headache"],
            data["skin_rash"],
            data["vomiting"],
            data["platelet_count"],
            data["joint_pain"],
            data["nausea"],
            data["travel_history"],
            data["symptom_score"]
        ))
        conn.commit()


def load_records():
    with sqlite3.connect(DB_NAME) as conn:
        return pd.read_sql_query(
            "SELECT * FROM patient_records ORDER BY id DESC",
            conn
        )


init_database()


# ==================================================
# LIVE WEATHER: OPEN-METEO
# ==================================================
@st.cache_data(ttl=900, show_spinner=False)
def get_weather():
    # Bengaluru coordinates
    url = (
        "https://api.open-meteo.com/v1/forecast"
        "?latitude=12.9716&longitude=77.5946"
        "&current=temperature_2m,relative_humidity_2m,"
        "precipitation,wind_speed_10m"
        "&timezone=Asia%2FKolkata"
    )

    request = urllib.request.Request(
        url,
        headers={"User-Agent": "DengueAIGuardian/1.0"}
    )

    with urllib.request.urlopen(request, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


# ==================================================
# GOVERNMENT DATA SOURCE
# ==================================================
@st.cache_data(ttl=3600, show_spinner=False)
def get_government_page():
    url = "https://ncvbdc.mohfw.gov.in/"
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0"}
    )

    with urllib.request.urlopen(request, timeout=15) as response:
        return response.read()


# ==================================================
# SIDEBAR NAVIGATION
# ==================================================
with st.sidebar:
    st.markdown("# 🩺 Dengue AI")
    st.markdown("### GUARDIAN")
    st.markdown("---")
    st.markdown("## Navigation")

    page = st.radio(
        "Select a section",
        [
            "Dashboard",
            "Symptom Assessment",
            "Government Statistics",
            "Patient Records",
            "About & Safety"
        ],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown("**Public Health Information System**")
    st.caption("Educational support tool — not a medical diagnosis.")
    st.markdown("---")
    st.caption("Dengue AI Guardian | Version 1.0")


# ==================================================
# DASHBOARD
# ==================================================
if page == "Dashboard":

    st.markdown("""
    <div class="app-banner">
        <h2> Dengue AI Guardian </h2>
        <p>Dengue Risk Assessment & Public Health Insights</p>
    </div>
    """, unsafe_allow_html=True)

    st.write(
        "Welcome to the healthcare information dashboard. "
        "Review weather conditions, assess reported symptoms, "
        "and explore published public-health information."
    )

    col1, col2, col3 = st.columns(3)

    try:
        weather = get_weather()
        current = weather.get("current", {})

        with col1:
            st.metric(
                "Temperature",
                f'{current.get("temperature_2m", "N/A")} °C'
            )

        with col2:
            st.metric(
                "Relative Humidity",
                f'{current.get("relative_humidity_2m", "N/A")} %'
            )

        with col3:
            st.metric(
                "Precipitation",
                f'{current.get("precipitation", "N/A")} mm'
            )

        st.caption(
            "Weather source: Open-Meteo API · Bengaluru. "
            "Weather conditions do not diagnose or predict an individual "
            "person's dengue infection."
        )

    except Exception:
        st.warning(
            "Live weather data is temporarily unavailable. "
            "Please check your internet connection and try again."
        )

    st.markdown("---")
    st.subheader("Explore the platform")

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("### 🩺 Symptom Assessment")
        st.write(
            "Enter symptoms and available platelet-count information "
            "to receive cautious educational guidance."
        )

    with c2:
        st.markdown("### 📊 Government Statistics")
        st.write(
            "Visit the official government source for published "
            "dengue surveillance information."
        )

    st.info(
        "If dengue is suspected, consult a qualified healthcare "
        "professional. Do not delay medical care based on this app."
    )


# ==================================================
# SYMPTOM ASSESSMENT
# ==================================================
elif page == "Symptom Assessment":

    st.title("Symptom Assessment")
    st.write(
        "Enter the available information below. "
        "This tool uses a simple, unvalidated rule-based score; "
        "it is not a trained machine-learning model."
    )

    with st.form("assessment_form"):

        st.subheader("Patient Information")

        col1, col2 = st.columns(2)

        with col1:
            fever = st.number_input(
                "Body temperature (°C)",
                min_value=30.0,
                max_value=45.0,
                value=37.0,
                step=0.1
            )

            headache = st.selectbox(
                "Headache",
                ["No", "Mild", "Severe"]
            )

            rash = st.selectbox(
                "Skin rash",
                ["No", "Yes"]
            )

            vomiting = st.selectbox(
                "Vomiting",
                ["No", "Yes"]
            )

        with col2:
            platelet_count = st.number_input(
                "Platelet count (per µL, if known)",
                min_value=0,
                max_value=1000000,
                value=0,
                step=1000,
                help="Enter 0 if you do not have a platelet report."
            )

            joint_pain = st.selectbox(
                "Joint or muscle pain",
                ["No", "Yes"]
            )

            nausea = st.selectbox(
                "Nausea",
                ["No", "Yes"]
            )

            travel_history = st.selectbox(
                "Recent travel to a dengue-prone area",
                ["No", "Yes"]
            )

        submitted = st.form_submit_button(
            "Assess Symptoms",
            use_container_width=True
        )

    if submitted:

        # This is an educational score, NOT a validated prediction.
        score = 0

        if fever >= 38:
            score += 2

        if headache == "Severe":
            score += 2
        elif headache == "Mild":
            score += 1

        if rash == "Yes":
            score += 1

        if vomiting == "Yes":
            score += 1

        if 0 < platelet_count < 150000:
            score += 2

        if joint_pain == "Yes":
            score += 1

        if nausea == "Yes":
            score += 1

        if travel_history == "Yes":
            score += 1

        record = {
            "fever_temp": fever,
            "headache": headache,
            "skin_rash": rash,
            "vomiting": vomiting,
            "platelet_count": platelet_count,
            "joint_pain": joint_pain,
            "nausea": nausea,
            "travel_history": travel_history,
            "symptom_score": score
        }

        try:
            save_record(record)
            st.success("Assessment record saved.")
        except Exception:
            st.error("The record could not be saved.")

        st.subheader("Assessment Summary")
        st.metric("Educational symptom score", score)

        st.warning(
            "This score is not medically validated and cannot determine "
            "whether you have dengue. A low score does not rule out dengue."
        )

        if vomiting == "Yes":
            st.warning(
                "Seek medical advice promptly, especially if vomiting "
                "is repeated or you cannot keep fluids down."
            )

        if 0 < platelet_count < 100000:
            st.warning(
                "This platelet count needs prompt medical review. "
                "A clinician must interpret it alongside symptoms and "
                "other test results."
            )

        st.markdown("### Emergency warning signs")

        st.write(
            "Seek urgent medical care for severe abdominal pain, "
            "persistent vomiting, bleeding, difficulty breathing, "
            "confusion, fainting, extreme drowsiness, or cold/clammy skin. "
            "Do not wait for an app result."
        )

        st.info(
            "A healthcare professional may recommend a dengue test "
            "and other blood tests based on your illness timeline."
        )


# ==================================================
# GOVERNMENT STATISTICS
# ==================================================
elif page == "Government Statistics":

    st.title("Government Dengue Information")
    st.write(
        "Use official government sources to review published dengue "
        "surveillance reports. These reports may be updated periodically "
        "and are not necessarily live case feeds."
    )

    st.markdown("### Official source")

    st.markdown(
        "[National Centre for Vector Borne Diseases Control (NCVBDC)]"
        "(https://ncvbdc.mohfw.gov.in/)"
    )

    if st.button("Check Government Website", use_container_width=True):
        try:
            with st.spinner("Connecting to the official website..."):
                page_bytes = get_government_page()

            st.success("The official government website responded.")

            try:
                tables = pd.read_html(BytesIO(page_bytes))

                if tables:
                    st.write(
                        "Tables found on the page. Check the source "
                        "and reporting date before interpreting the figures."
                    )

                    for i, table in enumerate(tables[:5]):
                        st.markdown(f"**Table {i + 1}**")
                        st.dataframe(table, use_container_width=True)

                else:
                    st.info(
                        "The page responded, but no readable tables were "
                        "found on its homepage. Open the official website "
                        "above and look for the latest dengue reports."
                    )

            except Exception:
                st.info(
                    "The website responded, but its data could not be "
                    "automatically extracted. Please view the official "
                    "reports directly using the link above."
                )

        except Exception:
            st.error(
                "Could not connect right now. Please open the official "
                "NCVBDC website directly and check your internet connection."
            )

    st.caption(
        "No statistics are fabricated or generated by this page. "
        "Only data actually retrieved from the official website is shown."
    )


# ==================================================
# PATIENT RECORDS
# ==================================================
elif page == "Patient Records":

    st.title("Patient Assessment Records")
    st.write(
        "This page shows assessments saved in this app's SQLite database."
    )

    try:
        records = load_records()

        if records.empty:
            st.info(
                "No records saved yet. Complete a symptom assessment "
                "to create a record."
            )
        else:
            st.metric("Saved records", len(records))
            st.dataframe(records, use_container_width=True)

            csv_data = records.to_csv(index=False).encode("utf-8")

            st.download_button(
                "Download Records as CSV",
                data=csv_data,
                file_name="dengue_assessment_records.csv",
                mime="text/csv",
                use_container_width=True
            )

            st.warning(
                "Privacy notice: do not enter names, phone numbers, "
                "addresses, or other identifying information. This demo "
                "does not provide production-grade patient-data security."
            )

    except Exception:
        st.error("Unable to load saved records.")


# ==================================================
# ABOUT & SAFETY
# ==================================================
elif page == "About & Safety":

    st.title("About Dengue AI Guardian")

    st.write(
        "Dengue AI Guardian is an educational project designed to "
        "organize symptom information, display weather data, and provide "
        "links to public-health resources."
    )

    st.subheader("Current capabilities")

    st.markdown("""
    - Symptom entry and educational scoring
    - Optional platelet-count entry
    - Live weather retrieval from Open-Meteo
    - Link to official government dengue information
    - Local SQLite assessment records
    """)

    st.subheader("Medical safety")

    st.warning(
        "This application is not a medical device, a validated diagnostic "
        "system, or a trained machine-learning model. Its score cannot "
        "confirm or exclude dengue."
    )

    st.write(
        "A clinician should interpret symptoms and laboratory results. "
        "Seek urgent medical care for warning signs such as severe "
        "abdominal pain, persistent vomiting, bleeding, breathing "
        "difficulty, confusion, fainting, or cold/clammy skin."
    )

    st.subheader("Data and privacy")

    st.write(
        "The current demo stores assessment information in a local SQLite "
        "file. On a hosted platform, local files may not persist across "
        "restarts or redeployments. This storage is not suitable for "
        "real patient records without additional security and privacy "
        "protections."
    )

    st.markdown(
        "**Weather source:** "
        "[Open-Meteo](https://open-meteo.com/)  \n"
        "**Government information:** "
        "[NCVBDC](https://ncvbdc.mohfw.gov.in/)"
    )


# ==================================================
# FOOTER
# ==================================================
st.markdown("---")
st.caption(
    "Dengue AI Guardian · Educational public-health project · "
    "Not a substitute for professional medical advice"
)
