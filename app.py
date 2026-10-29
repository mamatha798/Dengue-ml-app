import streamlit as st
import sqlite3
import json
import urllib.request
from datetime import datetime
from io import BytesIO
import pandas as pd

# ==================================================
# PAGE CONFIGURATION
# ==================================================
st.set_page_config(
    page_title="Dengue AI Guardian | Health Dashboard",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================================================
# PROFESSIONAL HEALTHCARE DESIGN
# ==================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}
.stApp {
    background: #f4f7fb;
}
.block-container {
    max-width: 1250px;
    padding-top: 1.8rem;
    padding-bottom: 3rem;
}
.hero {
    background: linear-gradient(120deg, #073b4c, #087f8c);
    padding: 30px;
    border-radius: 20px;
    color: white;
    margin-bottom: 24px;
}
.hero h1 {
    color: white;
    font-size: 34px;
    margin-bottom: 8px;
}
.hero p {
    color: #d8f3f4;
    font-size: 15px;
}
.section-title {
    color: #073b4c;
    font-size: 23px;
    font-weight: 750;
    margin-top: 15px;
    margin-bottom: 8px;
}
.metric-card {
    background: white;
    border: 1px solid #e1e9f0;
    border-radius: 15px;
    padding: 19px;
    min-height: 110px;
}
.metric-label {
    color: #637487;
    font-size: 13px;
    margin-bottom: 8px;
}
.metric-value {
    color: #073b4c;
    font-size: 27px;
    font-weight: 800;
}
.info-card {
    background: white;
    border: 1px solid #e1e9f0;
    border-radius: 15px;
    padding: 22px;
}
.small-note {
    color: #65758b;
    font-size: 12px;
}
div.stButton > button {
    background: #087f8c;
    color: white;
    border: 0;
    border-radius: 10px;
    min-height: 46px;
    font-weight: 700;
}
div.stButton > button:hover {
    background: #075c68;
    color: white;
}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ==================================================
# DATABASE
# ==================================================
DB_NAME = "dengue_guardian.db"


def get_connection():
    conn = sqlite3.connect(DB_NAME, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


def create_tables():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS patient_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                record_date TEXT NOT NULL,
                fever_temp REAL NOT NULL,
                headache TEXT NOT NULL,
                skin_rash TEXT NOT NULL,
                vomiting TEXT NOT NULL,
                platelet_count INTEGER NOT NULL,
                joint_pain TEXT NOT NULL,
                nausea TEXT NOT NULL,
                travel_history TEXT NOT NULL,
                symptom_score INTEGER NOT NULL
            )
        """)


def save_record(data):
    with get_connection() as conn:
        cursor = conn.execute("""
            INSERT INTO patient_records (
                record_date, fever_temp, headache, skin_rash,
                vomiting, platelet_count, joint_pain, nausea,
                travel_history, symptom_score
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(timespec="seconds"),
            data["fever_temp"],
            data["headache"],
            data["skin_rash"],
            data["vomiting"],
            data["platelets"],
            data["joint_pain"],
            data["nausea"],
            data["travel_history"],
            data["score"]
        ))
        return cursor.lastrowid


create_tables()

# ==================================================
# LIVE WEATHER API
# ==================================================
@st.cache_data(ttl=900, show_spinner=False)
def get_weather():
    url = (
        "https://api.open-meteo.com/v1/forecast"
        "?latitude=12.9716&longitude=77.5946"
        "&current=temperature_2m,relative_humidity_2m,precipitation"
        "&timezone=Asia%2FKolkata"
    )
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "DengueAIGuardian/1.0"}
    )
    with urllib.request.urlopen(request, timeout=12) as response:
        return json.loads(response.read().decode("utf-8"))


# ==================================================
# OFFICIAL NCVBDC STATISTICS
# ==================================================
GOV_URL = (
    "https://ncvbdc.mohfw.gov.in/index4.php"
    "?Background=Light&lang=1&level=0"
    "&lid=3715&linkid=431"
)


@st.cache_data(ttl=3600, show_spinner=False)
def get_karnataka_data():
    request = urllib.request.Request(
        GOV_URL,
        headers={"User-Agent": "Mozilla/5.0 DengueAIGuardian/1.0"}
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        html = response.read()

    tables = pd.read_html(BytesIO(html), header=None)
    if not tables:
        raise ValueError("No tables found on the official page.")

    df = tables[0]

    for _, row in df.iterrows():
        values = row.astype(str).str.strip()
        if values.str.fullmatch(
            "Karnataka", case=False, na=False
        ).any():
            years = [2021, 2022, 2023, 2024, 2025, 2026]
            result = []

            for i, year in enumerate(years):
                case_index = 2 + (i * 2)
                death_index = 3 + (i * 2)

                if death_index >= len(row):
                    continue

                result.append({
                    "Year": year,
                    "Reported cases": row.iloc[case_index],
                    "Reported deaths": row.iloc[death_index]
                })

            if result:
                return pd.DataFrame(result)

    raise ValueError("Karnataka row not found in the official table.")


# ==================================================
# HEADER
# ==================================================
st.markdown("""
<div class="hero">
    <h1>🩺 Dengue AI Guardian</h1>
    <p>Digital Dengue Awareness & Symptom Assessment Platform</p>
    <p>Public health information • Symptom recording • Safety guidance</p>
</div>
""", unsafe_allow_html=True)

st.sidebar.title("🩺 Dengue Guardian")
page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Symptom Assessment",
        "Government Statistics",
        "Patient Records",
        "About & Safety"
    ]
)

st.sidebar.markdown("---")
st.sidebar.caption("Educational decision-support prototype")
st.sidebar.caption("Not a substitute for medical care.")

# ==================================================
# DASHBOARD
# ==================================================
if page == "Dashboard":
    st.markdown(
        '<div class="section-title">Public Health Dashboard</div>',
        unsafe_allow_html=True
    )
    st.write(
        "Explore current Bengaluru weather, official published "
        "dengue statistics and symptom assessment."
    )

    col1, col2, col3 = st.columns(3)

    try:
        weather = get_weather()
        current = weather.get("current", {})

        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">🌡️ Bengaluru Temperature</div>
                <div class="metric-value">{current.get("temperature_2m", "N/A")} °C</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">💧 Relative Humidity</div>
                <div class="metric-value">{current.get("relative_humidity_2m", "N/A")}%</div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">🌧️ Precipitation</div>
                <div class="metric-value">{current.get("precipitation", "N/A")} mm</div>
            </div>
            """, unsafe_allow_html=True)

        st.caption(
            "Weather source: Open-Meteo. "
            f"Observation time: {current.get('time', 'Not available')}. "
            "Weather alone cannot predict an individual's dengue infection."
        )

    except Exception:
        st.warning(
            "Live weather is temporarily unavailable. "
            "Please try again later."
        )

    st.markdown("---")
    st.markdown(
        '<div class="section-title">Official Karnataka Dengue Statistics</div>',
        unsafe_allow_html=True
    )

    try:
        stats = get_karnataka_data()
        st.dataframe(stats, hide_index=True, use_container_width=True)
        st.caption(
            "Source: National Centre for Vector Borne Diseases Control (NCVBDC), "
            "Government of India. These are published figures, not a live case feed. "
            "The latest reporting period should be verified at the source."
        )
        st.markdown(f"[Open official source]({GOV_URL})")
    except Exception:
        st.warning(
            "Official statistics could not be fetched right now. "
            "Please open the government source directly."
        )
        st.markdown(f"[NCVBDC official source]({GOV_URL})")

    st.info(
        "Prevention: remove standing water, cover water-storage containers, "
        "use mosquito repellent and wear protective clothing."
    )

# ==================================================
# SYMPTOM ASSESSMENT
# ==================================================
elif page == "Symptom Assessment":
    st.markdown(
        '<div class="section-title">Symptom Assessment</div>',
        unsafe_allow_html=True
    )
    st.write(
        "Enter the requested information. This form records symptoms "
        "and provides safety guidance; it does not diagnose dengue."
    )

    with st.form("symptom_form"):
        left, right = st.columns(2)

        with left:
            fever = st.number_input(
                "Body temperature (°C)",
                min_value=35.0,
                max_value=42.0,
                value=37.0,
                step=0.1
            )
            headache = st.selectbox(
                "Headache", ["No", "Mild", "Severe"]
            )
            rash = st.selectbox("Skin rash", ["No", "Yes"])
            vomiting = st.selectbox("Vomiting", ["No", "Yes"])

        with right:
            platelets = st.number_input(
                "Platelet count (cells/µL, if known)",
                min_value=10000,
                max_value=500000,
                value=250000,
                step=1000
            )
            joint_pain = st.selectbox(
                "Joint or muscle pain", ["No", "Yes"]
            )
            nausea = st.selectbox("Nausea", ["No", "Yes"])
            travel = st.selectbox(
                "Recent travel to a dengue-prone area",
                ["No", "Yes"]
            )

        submitted = st.form_submit_button(
            "Save Assessment & View Guidance",
            use_container_width=True
        )

    if submitted:
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
        if platelets < 150000:
            score += 2
        if joint_pain == "Yes":
            score += 1
        if nausea == "Yes":
            score += 1
        if travel == "Yes":
            score += 1

        data = {
            "fever_temp": fever,
            "headache": headache,
            "skin_rash": rash,
            "vomiting": vomiting,
            "platelets": int(platelets),
            "joint_pain": joint_pain,
            "nausea": nausea,
            "travel_history": travel,
            "score": score
        }

        try:
            record_id = save_record(data)
            st.success(f"Assessment record saved. Record ID: {record_id}")
        except Exception:
            st.error(
                "The record could not be saved. Please try again."
            )

        st.markdown("### Assessment Summary")
        st.write(f"Reported symptoms: {score} score points.")
        st.warning(
            "This score is an unvalidated demonstration rule, not a trained "
            "machine-learning model and not a medically validated dengue risk score. "
            "It cannot confirm or rule out dengue. Seek clinical assessment "
            "if you have concerning symptoms."
        )

        if fever >= 38:
            st.info(
                "Fever can have many causes, including dengue. "
                "Contact a healthcare professional for assessment."
            )

        if platelets < 150000:
            st.warning(
                "A low platelet count needs interpretation by a healthcare "
                "professional. Do not use this app alone to assess severity."
            )

        if vomiting == "Yes":
            st.warning(
                "Persistent vomiting is a warning sign requiring urgent medical evaluation."
            )

        st.error(
            "URGENT: Severe abdominal pain, persistent vomiting, bleeding, "
            "difficulty breathing, confusion, fainting, or cold/clammy skin "
            "need urgent medical care. Do not wait for this app."
        )

# ==================================================
# GOVERNMENT STATISTICS
# ==================================================
elif page == "Government Statistics":
    st.markdown(
        '<div class="section-title">Official Dengue Statistics</div>',
        unsafe_allow_html=True
    )
    st.write(
        "Published Karnataka dengue case and death figures from the "
        "Government of India's NCVBDC website."
    )

    if st.button("Refresh official data"):
        get_karnataka_data.clear()

    try:
        stats = get_karnataka_data()
        st.dataframe(stats, hide_index=True, use_container_width=True)

        try:
            chart_data = stats.copy()
            chart_data["Reported cases"] = pd.to_numeric(
                chart_data["Reported cases"], errors="coerce"
            )
            st.bar_chart(
                chart_data.set_index("Year")[["Reported cases"]]
            )
        except Exception:
            st.caption("A chart could not be created from the published table.")

    except Exception as error:
        st.error("Could not retrieve the official table right now.")
        st.caption(str(error))

    st.markdown(f"[Visit NCVBDC Government Website]({GOV_URL})")
    st.caption(
        "Reporting dates and provisional figures can affect year-to-year "
        "comparisons. Check the original government publication."
    )

# ==================================================
# PATIENT RECORDS
# ==================================================
elif page == "Patient Records":
    st.markdown(
        '<div class="section-title">Saved Assessment Records</div>',
        unsafe_allow_html=True
    )
    st.warning(
        "Prototype privacy notice: do not enter identifiable or real patient "
        "information in this public demo. SQLite storage on a hosted app may "
        "not be durable across restarts or redeployments."
    )

    try:
        with get_connection() as conn:
            records = pd.read_sql_query(
                """
                SELECT id, record_date, fever_temp, headache,
                       skin_rash, vomiting, platelet_count,
                       joint_pain, nausea, travel_history, symptom_score
                FROM patient_records
                ORDER BY id DESC
                LIMIT 100
                """,
                conn
            )

        if records.empty:
            st.info("No assessment records have been saved in this app instance.")
        else:
            st.write(f"Showing {len(records)} most recent records.")
            st.dataframe(
                records,
                hide_index=True,
                use_container_width=True
            )

    except Exception:
        st.error("Records could not be loaded.")

# ==================================================
# ABOUT & SAFETY
# ==================================================
elif page == "About & Safety":
    st.markdown(
        '<div class="section-title">About Dengue AI Guardian</div>',
        unsafe_allow_html=True
    )

    st.markdown("""
    **Purpose**

    This prototype brings together public weather information, published
    government statistics and a basic symptom-recording form.

    **Data sources**
    - Weather: Open-Meteo forecast API.
    - Published dengue statistics: NCVBDC, Government of India.
    - Symptom records: SQLite database in the application environment.

    **Important limitations**
    - This application does not contain a trained or clinically validated ML model.
    - The symptom score is a demonstration rule, not a probability of dengue.
    - Weather and state-level statistics cannot determine whether an individual
      has dengue.
    - Platelet counts must be interpreted in clinical context.
    - Hosted SQLite storage may not persist reliably after app restarts or redeployments.

    **Emergency guidance**

    Severe abdominal pain, persistent vomiting, bleeding, difficulty breathing,
    confusion, fainting or cold/clammy skin require urgent medical evaluation.

    Do not delay professional medical care while using this application.
    """)

    st.markdown(
        "[NCVBDC official website](https://ncvbdc.mohfw.gov.in/)"
    )

# ==================================================
# FOOTER
# ==================================================
st.markdown("---")
st.caption(
    "Dengue AI Guardian • Educational prototype • "
    "Not a medical diagnostic device • Consult a qualified healthcare professional."
)
