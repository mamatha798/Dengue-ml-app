import sqlite3
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests
import streamlit as st

# ------------------------------------------------------------
# Dengue AI Guardian — educational screening dashboard
# ------------------------------------------------------------
st.set_page_config(
    page_title="Dengue AI Guardian",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

DB_PATH = Path(__file__).with_name("dengue_data.db")
WARNING_DEFAULT = "None reported"


# ----------------------------- Styling -----------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: Inter, sans-serif; }
    .stApp { background: #f4f8fb; }
    [data-testid="stSidebar"] { background: #102a43; }
    [data-testid="stSidebar"] * { color: #f4f8fb !important; }
    [data-testid="stMain"] label,
    [data-testid="stMain"] [data-testid="stWidgetLabel"],
    [data-testid="stMain"] [data-testid="stWidgetLabel"] p {
        color: #17324d !important;
        font-weight: 600 !important;
    }
    [data-testid="stMain"] { color: #17324d; }
    .hero {
        padding: 1.5rem 1.6rem; border-radius: 18px;
        background: linear-gradient(120deg, #123b55, #087e8b);
        color: white; margin-bottom: 1rem;
    }
    .hero h1 { color: white; margin: 0; font-size: 2rem; }
    .hero p { color: #e6f7fa; margin: .4rem 0 0 0; }
    .small-note { color: #526777; font-size: .9rem; }
    div[data-testid="stMetric"] {
        background: white; border: 1px solid #dce7ee;
        padding: 14px; border-radius: 14px;
    }
    div.stButton > button[kind="primary"] {
        background: #087e8b; border: 0; color: white;
        border-radius: 10px; font-weight: 700;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ----------------------------- Database ----------------------
def get_connection():
    conn = sqlite3.connect(str(DB_PATH), timeout=20)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    """Create the table if missing and safely add missing columns to old DBs."""
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS patient_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                record_date TEXT NOT NULL,
                temperature REAL,
                headache TEXT,
                rash TEXT,
                vomiting TEXT,
                joint_pain TEXT,
                nausea TEXT,
                travel_history TEXT,
                platelet_count INTEGER,
                warning_signs TEXT DEFAULT 'None reported',
                symptom_score INTEGER DEFAULT 0
            )
            """
        )

        existing = {
            row["name"]
            for row in conn.execute("PRAGMA table_info(patient_records)").fetchall()
        }

        # Add columns missing from an older version without deleting existing rows.
        required = {
            "record_date": "TEXT",
            "temperature": "REAL",
            "headache": "TEXT",
            "rash": "TEXT",
            "vomiting": "TEXT",
            "joint_pain": "TEXT",
            "nausea": "TEXT",
            "travel_history": "TEXT",
            "platelet_count": "INTEGER",
            "warning_signs": "TEXT DEFAULT 'None reported'",
            "symptom_score": "INTEGER DEFAULT 0",
        }
        for column, sql_type in required.items():
            if column not in existing:
                conn.execute(f"ALTER TABLE patient_records ADD COLUMN {column} {sql_type}")

        conn.execute(
            "UPDATE patient_records SET warning_signs = ? WHERE warning_signs IS NULL",
            (WARNING_DEFAULT,),
        )
        conn.execute(
            "UPDATE patient_records SET symptom_score = 0 WHERE symptom_score IS NULL"
        )


initialize_database()


# ----------------------------- Helpers ------------------------
def get_records():
    with get_connection() as conn:
        return pd.read_sql_query(
            "SELECT * FROM patient_records ORDER BY id DESC", conn
        )


def save_assessment(values):
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO patient_records (
                record_date, temperature, headache, rash, vomiting,
                joint_pain, nausea, travel_history, platelet_count,
                warning_signs, symptom_score
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                values["temperature"],
                values["headache"],
                values["rash"],
                values["vomiting"],
                values["joint_pain"],
                values["nausea"],
                values["travel_history"],
                values["platelet_count"],
                values["warning_signs"],
                values["symptom_score"],
            ),
        )


def fetch_weather():
    """Open-Meteo current conditions for Bengaluru; no API key required."""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": 12.9716,
        "longitude": 77.5946,
        "current": "temperature_2m,relative_humidity_2m,precipitation",
        "timezone": "Asia/Kolkata",
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        current = data.get("current", {})
        return {
            "temperature": current.get("temperature_2m"),
            "humidity": current.get("relative_humidity_2m"),
            "precipitation": current.get("precipitation"),
            "time": current.get("time", "Not supplied"),
        }, None
    except (requests.RequestException, ValueError) as exc:
        return None, str(exc)


def symptom_score(values):
    """Transparent symptom count for education, not a trained ML prediction."""
    keys = ("headache", "rash", "vomiting", "joint_pain", "nausea")
    return sum(1 for key in keys if values[key] == "Yes")


def show_emergency_message(warning_signs):
    if warning_signs != WARNING_DEFAULT:
        st.error(
            "⚠️ A warning sign was selected. Please seek urgent medical assessment "
            "now. If the person is very drowsy, confused, fainting, has severe "
            "abdominal pain, persistent vomiting, bleeding, breathing difficulty, "
            "or cold/clammy skin, contact local emergency services immediately."
        )


# ----------------------------- Sidebar ------------------------
with st.sidebar:
    st.markdown("## 🩺 Dengue AI Guardian")
    st.caption("Awareness • Screening • Prevention")
    page = st.radio(
        "Navigate",
        [
            "Dashboard",
            "Symptom Assessment",
            "Patient Records",
            "Weather Monitor",
            "Food & Prevention",
            "Government Information",
            "About & Safety",
        ],
    )
    st.divider()
    st.caption("Educational support only — not a medical diagnosis.")


# ----------------------------- Header -------------------------
st.markdown(
    """
    <div class="hero">
      <h1>🩺 Dengue AI Guardian</h1>
      <p>Understand symptoms, record assessments, monitor local weather,
      and learn practical prevention steps.</p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ----------------------------- Dashboard ----------------------
if page == "Dashboard":
    st.subheader("Dashboard")
    st.write("Monitor saved assessments, current weather and dengue prevention guidance.")
    records = get_records()

    total = len(records)
    warning_count = 0
    if not records.empty and "warning_signs" in records.columns:
        warning_count = int(
            records["warning_signs"]
            .fillna(WARNING_DEFAULT)
            .ne(WARNING_DEFAULT)
            .sum()
        )

    c1, c2, c3 = st.columns(3)
    c1.metric("Saved assessments", total)
    c2.metric("Assessments with warning signs", warning_count)
    c3.metric("Weather data", "Live check available")

    st.markdown("### Recent assessments")
    if records.empty:
        st.info("No assessments saved yet. Open Symptom Assessment to add one.")
    else:
        display_cols = [
            col for col in [
                "record_date", "temperature", "platelet_count",
                "symptom_score", "warning_signs"
            ] if col in records.columns
        ]
        st.dataframe(records[display_cols].head(10), use_container_width=True, hide_index=True)

    st.markdown("### Important")
    st.info(
        "Dengue cannot be confirmed from symptoms or weather alone. A healthcare "
        "professional may recommend examination and blood tests based on the person's condition."
    )


# ----------------------------- Symptom Assessment -------------
elif page == "Symptom Assessment":
    st.subheader("Symptom Assessment")
    st.write("Enter information to create an educational symptom summary and save a record.")

    with st.form("assessment_form"):
        col1, col2 = st.columns(2)
        with col1:
            temperature = st.number_input(
                "Body temperature (°C)", min_value=30.0, max_value=45.0,
                value=37.0, step=0.1, help="Enter the measured temperature if known."
            )
            headache = st.radio("Headache", ["No", "Yes"], horizontal=True)
            rash = st.radio("Skin rash", ["No", "Yes"], horizontal=True)
            vomiting = st.radio("Vomiting", ["No", "Yes"], horizontal=True)
        with col2:
            joint_pain = st.radio("Joint or muscle pain", ["No", "Yes"], horizontal=True)
            nausea = st.radio("Nausea", ["No", "Yes"], horizontal=True)
            travel_history = st.selectbox(
                "Recent travel to an area with dengue activity?",
                ["Unknown", "No", "Yes"],
            )
            platelet_count = st.number_input(
                "Platelet count (if available)", min_value=0, max_value=1000000,
                value=0, step=1000, help="Enter 0 if you do not have a report."
            )

        warning_options = [
            "None reported",
            "Severe abdominal pain",
            "Persistent vomiting",
            "Bleeding from nose/gums or other bleeding",
            "Drowsiness, confusion or restlessness",
            "Difficulty breathing",
            "Cold/clammy skin or fainting",
        ]
        warning_signs = st.selectbox("Warning signs (choose the most urgent one)", warning_options)
        submitted = st.form_submit_button("Assess and Save Record", type="primary")

    if submitted:
        values = {
            "temperature": float(temperature),
            "headache": headache,
            "rash": rash,
            "vomiting": vomiting,
            "joint_pain": joint_pain,
            "nausea": nausea,
            "travel_history": travel_history,
            "platelet_count": int(platelet_count) if platelet_count > 0 else None,
            "warning_signs": warning_signs,
        }
        values["symptom_score"] = symptom_score(values)
        try:
            save_assessment(values)
            st.success("Assessment saved to the app's SQLite database.")
        except sqlite3.Error as exc:
            st.error(f"Could not save this record: {exc}")

        show_emergency_message(warning_signs)
        st.markdown("### Summary")
        st.write(f"Symptoms marked 'Yes': **{values['symptom_score']} of 5**")
        if temperature >= 38:
            st.warning("A raised temperature was entered. Consider contacting a healthcare professional, especially if symptoms persist or worsen.")
        if platelet_count > 0:
            st.write(f"Platelet count entered: **{int(platelet_count):,}**")
            st.caption("Only a clinician can interpret this result in context; one platelet value alone does not diagnose dengue.")
        st.info(
            "This is a symptom count only, not a trained machine-learning prediction and not a dengue diagnosis."
        )


# ----------------------------- Patient Records ----------------
elif page == "Patient Records":
    st.subheader("Patient Records")
    st.write("Records are stored in the SQLite database bundled with this app.")
    records = get_records()

    if records.empty:
        st.info("No patient records have been saved yet.")
    else:
        st.dataframe(records, use_container_width=True, hide_index=True)
        csv_bytes = records.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download records as CSV",
            data=csv_bytes,
            file_name="dengue_patient_records.csv",
            mime="text/csv",
        )
        st.caption(
            "Privacy: avoid entering names, phone numbers, addresses or other direct identifiers. "
            "A local SQLite file on a hosted app may not be durable across restarts/redeployments."
        )


# ----------------------------- Weather Monitor ----------------
elif page == "Weather Monitor":
    st.subheader("Bengaluru Weather Monitor")
    st.write("Current weather is fetched from Open-Meteo when you press the button.")
    if st.button("Fetch current weather", type="primary"):
        with st.spinner("Fetching weather…"):
            weather, error = fetch_weather()
        if error:
            st.warning("Weather data could not be fetched right now. Check your connection and try again.")
            st.caption(error)
        elif weather:
            a, b, c = st.columns(3)
            a.metric("Temperature", f"{weather['temperature']} °C" if weather["temperature"] is not None else "N/A")
            b.metric("Relative humidity", f"{weather['humidity']}%" if weather["humidity"] is not None else "N/A")
            c.metric("Precipitation", f"{weather['precipitation']} mm" if weather["precipitation"] is not None else "N/A")
            st.caption(f"Observation time: {weather['time']} (Asia/Kolkata)")
    st.info(
        "Weather conditions can inform mosquito-prevention awareness, but weather data cannot tell whether an individual has dengue."
    )


# ----------------------------- Food & Prevention --------------
elif page == "Food & Prevention":
    st.subheader("Food & Prevention")
    st.markdown("### Helpful general care")
    st.markdown(
        """
        - Drink fluids frequently; use oral rehydration solution if appropriate.
        - Eat tolerated foods such as rice, soup, porridge, fruit and other balanced meals.
        - Rest and monitor symptoms.
        - Use mosquito nets/repellent and remove standing water around the home.
        """
    )
    st.markdown("### Avoid unsafe self-treatment")
    st.markdown(
        """
        - Do not take aspirin or ibuprofen for suspected dengue unless a clinician specifically directs you; they can increase bleeding risk.
        - Do not self-medicate or rely on food, weather, or this app as a cure.
        - Seek medical advice about medicines, fluids and blood-test timing.
        """
    )
    st.error(
        "Urgent care is needed for severe abdominal pain, persistent vomiting, bleeding, "
        "difficulty breathing, confusion/drowsiness, fainting or cold/clammy skin."
    )


# ----------------------------- Government Information ---------
elif page == "Government Information":
    st.subheader("Official information")
    st.write("Use official public-health sources and follow advice from local healthcare professionals.")
    st.markdown(
        "- [National Centre for Vector Borne Diseases Control (NCVBDC)](https://ncvbdc.mohfw.gov.in/)\n"
        "- [World Health Organization — Dengue](https://www.who.int/news-room/fact-sheets/detail/dengue-and-severe-dengue)\n"
        "- [Open-Meteo weather API](https://open-meteo.com/)"
    )
    st.caption("Links are provided for information. Check current official guidance directly.")


# ----------------------------- About & Safety -----------------
elif page == "About & Safety":
    st.subheader("About Dengue AI Guardian")
    st.write(
        "This Streamlit prototype provides symptom recording, simple symptom counting, "
        "current Bengaluru weather and prevention education."
    )
    st.markdown("### What this app does")
    st.markdown(
        "- Saves assessment entries to SQLite.\n"
        "- Adds missing columns when an older `patient_records` database is opened.\n"
        "- Shows saved records and supports CSV export.\n"
        "- Fetches current weather from Open-Meteo on request."
    )
    st.markdown("### What this app does not do")
    st.markdown(
        "- It does not confirm or rule out dengue.\n"
        "- It does not currently run a validated/trained clinical ML model.\n"
        "- It does not replace a clinician, CBC interpretation, emergency service or hospital."
    )
    st.warning(
        "Do not delay medical care to use this app. If severe or rapidly worsening symptoms occur, seek urgent medical help."
    )

st.divider()
st.caption(
    "Dengue AI Guardian • Educational prototype • Keep personal health information private."
)
