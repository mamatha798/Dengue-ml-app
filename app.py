import streamlit as st
import sqlite3
import urllib.request
import json
from datetime import datetime
import pandas as pd

# =====================================================
# 1. PAGE CONFIGURATION
# =====================================================
st.set_page_config(
    page_title="Dengue AI Guardian",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

DB_NAME = "dengue_guardian.db"

# =====================================================
# 2. PROFESSIONAL DESIGN AND DROPDOWN FIX
# =====================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

[data-testid="stAppViewContainer"] {
    background: #F5F8FC;
}

[data-testid="stHeader"] {
    background: #F5F8FC;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #102A43;
    min-width: 280px;
}

[data-testid="stSidebar"] > div {
    background: #102A43;
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
    color: #FFFFFF;
}

[data-testid="stSidebar"] h1 {
    font-size: 25px !important;
    font-weight: 800 !important;
}

[data-testid="stSidebar"] h2 {
    font-size: 21px !important;
}

[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label {
    font-size: 17px !important;
    line-height: 1.6 !important;
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

p, li {
    line-height: 1.65;
}

/* Input fields */
div[data-baseweb="select"] > div {
    background-color: #FFFFFF !important;
    border-color: #CBD5E1 !important;
}

div[data-baseweb="select"] input {
    color: #102A43 !important;
    -webkit-text-fill-color: #102A43 !important;
}

/* Dropdown menu: readable Yes/No options */
div[data-baseweb="popover"],
div[data-baseweb="popover"] > div,
ul[role="listbox"] {
    background-color: #FFFFFF !important;
}

li[role="option"],
div[role="option"] {
    background-color: #FFFFFF !important;
    color: #102A43 !important;
    -webkit-text-fill-color: #102A43 !important;
    font-size: 16px !important;
}

li[role="option"] *,
div[role="option"] * {
    color: #102A43 !important;
    -webkit-text-fill-color: #102A43 !important;
}

li[role="option"]:hover,
div[role="option"]:hover {
    background-color: #E6F4F5 !important;
    color: #102A43 !important;
}

/* Buttons */
.stButton button,
.stFormSubmitButton button {
    min-height: 44px;
    border-radius: 8px;
    font-size: 16px !important;
    font-weight: 600 !important;
}

/* Metric cards */
div[data-testid="stMetric"] {
    background: #FFFFFF;
    padding: 18px;
    border: 1px solid #E1E8F0;
    border-radius: 12px;
}

div[data-testid="stMetricValue"] {
    color: #147D92;
    font-weight: 700;
}

/* Banner */
.app-banner {
    background: linear-gradient(110deg, #102A43, #147D92);
    padding: 25px;
    border-radius: 14px;
    margin-bottom: 20px;
}

.app-banner h2 {
    color: #FFFFFF !important;
    margin: 0;
}

.app-banner p {
    color: #FFFFFF;
    font-size: 16px;
}

hr {
    border-color: #DCE5EE;
}
</style>
""", unsafe_allow_html=True)


# =====================================================
# 3. DATABASE
# =====================================================
def init_database():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS patient_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                record_date TEXT,
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

        # Add any missing columns to an older version of this table.
        existing = {
            row[1] for row in
            conn.execute("PRAGMA table_info(patient_records)").fetchall()
        }

        needed_columns = {
            "record_date": "TEXT",
            "fever_temp": "REAL",
            "headache": "TEXT",
            "skin_rash": "TEXT",
            "vomiting": "TEXT",
            "platelet_count": "INTEGER",
            "joint_pain": "TEXT",
            "nausea": "TEXT",
            "travel_history": "TEXT",
            "symptom_score": "INTEGER"
        }

        for column, datatype in needed_columns.items():
            if column not in existing:
                conn.execute(
                    f"ALTER TABLE patient_records ADD COLUMN {column} {datatype}"
                )

        conn.commit()


def save_record(record):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
            INSERT INTO patient_records (
                record_date, fever_temp, headache, skin_rash,
                vomiting, platelet_count, joint_pain, nausea,
                travel_history, symptom_score
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            record["fever_temp"],
            record["headache"],
            record["skin_rash"],
            record["vomiting"],
            record["platelet_count"],
            record["joint_pain"],
            record["nausea"],
            record["travel_history"],
            record["symptom_score"]
        ))
        conn.commit()


def load_records():
    with sqlite3.connect(DB_NAME) as conn:
        return pd.read_sql_query(
            "SELECT * FROM patient_records ORDER BY id DESC",
            conn
        )


init_database()


# =====================================================
# 4. LIVE WEATHER
# =====================================================
@st.cache_data(ttl=900, show_spinner=False)
def get_weather():
    url = (
        "https://api.open-meteo.com/v1/forecast"
        "?latitude=12.9716&longitude=77.5946"
        "&current=temperature_2m,relative_humidity_2m,precipitation"
        "&timezone=Asia%2FKolkata"
    )

    request = urllib.request.Request(
        url, headers={"User-Agent": "DengueAIGuardian/1.0"}
    )

    with urllib.request.urlopen(request, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


# =====================================================
# 5. SIDEBAR NAVIGATION
# =====================================================
with st.sidebar:
    st.markdown("# 🩺 Dengue AI")
    st.markdown("## GUARDIAN")
    st.markdown("---")
    st.markdown("## Navigation")

    page = st.radio(
        "Choose a page",
        [
            "Dashboard",
            "Symptom Assessment",
            "Government Information",
            "Patient Records",
            "About & Safety"
        ],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.caption("Public Health Information Project")
    st.caption("Educational support only — not a diagnosis.")


# =====================================================
# 6. DASHBOARD
# =====================================================
if page == "Dashboard":

    st.markdown("""
    <div class="app-banner">
        <h2>Dengue AI Guardian</h2>
        <p>Dengue Risk Assessment & Public Health Insights</p>
    </div>
    """, unsafe_allow_html=True)

    st.write(
        "A healthcare information dashboard for symptom entry, "
        "weather observations, and public-health resources."
    )

    try:
        weather = get_weather()
        current = weather.get("current", {})

        c1, c2, c3 = st.columns(3)

        with c1:
            st.metric(
                "Temperature",
                f'{current.get("temperature_2m", "N/A")} °C'
            )

        with c2:
            st.metric(
                "Humidity",
                f'{current.get("relative_humidity_2m", "N/A")} %'
            )

        with c3:
            st.metric(
                "Precipitation",
                f'{current.get("precipitation", "N/A")} mm'
            )

        st.caption(
            "Source: Open-Meteo API · Bengaluru. Weather does not "
            "diagnose dengue or predict an individual's infection."
        )

    except Exception:
        st.warning(
            "Weather data is temporarily unavailable. "
            "Please check your internet connection."
        )

    st.markdown("---")
    st.subheader("Platform modules")

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("### 🩺 Symptom Assessment")
        st.write("Enter symptoms and available platelet information.")

    with c2:
        st.markdown("### 📊 Government Information")
        st.write("Visit the official source for published dengue reports.")

    st.info(
        "If dengue is suspected, consult a qualified healthcare "
        "professional. Do not delay care based on this app."
    )


# =====================================================
# 7. SYMPTOM ASSESSMENT
# =====================================================
elif page == "Symptom Assessment":

    st.title("Patient Symptom Assessment")
    st.write(
        "Enter the available information. The score below is an "
        "unvalidated educational rule, not a diagnostic or ML model."
    )

    with st.form("assessment_form"):

        st.subheader("Patient Information")

        c1, c2 = st.columns(2)

        with c1:
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

        with c2:
            platelet_count = st.number_input(
                "Platelet count (per µL; enter 0 if unknown)",
                min_value=0,
                max_value=1000000,
                value=0,
                step=1000
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
            "Submit Assessment",
            use_container_width=True
        )

    if submitted:
        score = 0

        # Educational score only; not clinically validated.
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
            st.success("Assessment record saved successfully.")
        except Exception:
            st.error("Could not save the assessment record.")

        st.subheader("Assessment Summary")
        st.metric("Unvalidated symptom score", score)

        st.warning(
            "This score cannot confirm or exclude dengue. A low score "
            "does not mean that a person is free from dengue."
        )

        if vomiting == "Yes":
            st.warning(
                "Seek medical advice promptly if vomiting is repeated "
                "or fluids cannot be kept down."
            )

        if 0 < platelet_count < 100000:
            st.warning(
                "This platelet count needs prompt clinical review. "
                "A healthcare professional must interpret the result."
            )

        st.subheader("Urgent warning signs")
        st.write(
            "Seek urgent medical care for severe abdominal pain, "
            "persistent vomiting, bleeding, breathing difficulty, "
            "confusion, fainting, extreme drowsiness, or cold/clammy skin."
        )

        st.info(
            "A healthcare professional can decide whether dengue testing "
            "and other blood tests are needed."
        )


# =====================================================
# 8. GOVERNMENT INFORMATION
# =====================================================
elif page == "Government Information":

    st.title("Official Dengue Information")

    st.write(
        "Published surveillance reports may be updated periodically "
        "and should not be treated as a live case count."
    )

    st.markdown(
        "[Open the National Centre for Vector Borne Diseases Control]"
        "(https://ncvbdc.mohfw.gov.in/)"
    )

    st.caption(
        "Use the official website to locate the latest available reports. "
        "This page does not invent or estimate case figures."
    )


# =====================================================
# 9. PATIENT RECORDS
# =====================================================
elif page == "Patient Records":

    st.title("Assessment Records")

    st.warning(
        "This demo database may not persist across hosted-app restarts. "
        "Do not enter names, phone numbers, addresses, or other "
        "identifying patient information."
    )

    try:
        records = load_records()

        if records.empty:
            st.info(
                "No records available yet. Submit an assessment first."
            )
        else:
            st.metric("Saved assessments", len(records))
            st.dataframe(records, use_container_width=True)

            st.download_button(
                "Download CSV",
                data=records.to_csv(index=False).encode("utf-8"),
                file_name="dengue_assessment_records.csv",
                mime="text/csv"
            )

    except Exception:
        st.error("Could not load records from the database.")


# =====================================================
# 10. ABOUT AND SAFETY
# =====================================================
elif page == "About & Safety":

    st.title("About Dengue AI Guardian")

    st.write(
        "This educational project organizes symptom information, "
        "displays weather observations, and links to public-health sources."
    )

    st.subheader("Current features")

    st.markdown("""
    - Symptom form
    - Educational rule-based score
    - Live weather data from Open-Meteo
    - Local SQLite assessment records
    - Official government information link
    """)

    st.subheader("Medical disclaimer")

    st.error(
        "This is not a validated diagnostic system and does not use "
        "a trained machine-learning model. It cannot diagnose dengue."
    )

    st.write(
        "Seek urgent medical care for severe abdominal pain, persistent "
        "vomiting, bleeding, difficulty breathing, confusion, fainting, "
        "or cold/clammy skin."
    )

    st.subheader("Data and privacy")

    st.write(
        "The demo stores assessment data in a local SQLite file. "
        "Hosted storage may be temporary. Production use requires "
        "appropriate security, access control, and privacy safeguards."
    )

    st.markdown(
        "[Open-Meteo weather service](https://open-meteo.com/)  \n"
        "[Government dengue information](https://ncvbdc.mohfw.gov.in/)"
    )


# =====================================================
# 11. FOOTER
# =====================================================
st.markdown("---")
st.caption(
    "Dengue AI Guardian | Educational public-health project | "
    "Not a substitute for professional medical advice"
)
