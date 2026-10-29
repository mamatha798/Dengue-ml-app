import os
import sqlite3
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests
import streamlit as st

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Dengue AI Guardian",
    page_icon="🦟",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --------------------------------------------------
# OPTIONAL SUPABASE CONNECTION
# --------------------------------------------------

supabase = None
SUPABASE_ERROR = None

try:
    from supabase import create_client

    try:
        supabase_url = st.secrets.get("SUPABASE_URL", "")
        supabase_key = st.secrets.get("SUPABASE_KEY", "")
    except Exception:
        supabase_url = os.getenv("SUPABASE_URL", "")
        supabase_key = os.getenv("SUPABASE_KEY", "")

    if supabase_url and supabase_key:
        supabase = create_client(supabase_url, supabase_key)

except Exception as exc:
    SUPABASE_ERROR = str(exc)

# --------------------------------------------------
# DATABASE CONFIGURATION
# --------------------------------------------------

DB_PATH = Path(__file__).parent / "dengue_guardian.db"


def init_database():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS patient_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                record_date TEXT NOT NULL,
                patient_name TEXT,
                age INTEGER,
                temperature REAL,
                headache INTEGER,
                rash INTEGER,
                vomiting INTEGER,
                joint_pain INTEGER,
                nausea INTEGER,
                travel_history INTEGER,
                platelet_count INTEGER,
                warning_signs INTEGER,
                symptom_score INTEGER,
                assessment TEXT
            )
            """
        )
        conn.commit()


def save_to_sqlite(record):
    columns = list(record.keys())
    placeholders = ", ".join(["?"] * len(columns))
    column_names = ", ".join(columns)

    query = (
        f"INSERT INTO patient_records ({column_names}) "
        f"VALUES ({placeholders})"
    )

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(query, list(record.values()))
        conn.commit()


def load_sqlite_records():
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query(
            "SELECT * FROM patient_records ORDER BY id DESC",
            conn,
        )


def save_record(record):
    if supabase is not None:
        try:
            supabase.table("patient_records").insert(record).execute()
            return True, "Supabase"
        except Exception as exc:
            try:
                save_to_sqlite(record)
                return True, "SQLite fallback"
            except Exception as sqlite_exc:
                return False, f"Database error: {sqlite_exc}"
    else:
        try:
            save_to_sqlite(record)
            return True, "SQLite"
        except Exception as exc:
            return False, str(exc)


def load_records():
    if supabase is not None:
        try:
            result = (
                supabase.table("patient_records")
                .select("*")
                .order("id", desc=True)
                .execute()
            )
            return pd.DataFrame(result.data), "Supabase"
        except Exception:
            pass

    return load_sqlite_records(), "SQLite"


init_database()

# --------------------------------------------------
# CUSTOM STYLING
# --------------------------------------------------

st.markdown(
    """
    <style>
    .main {
        background-color: #f7f9fc;
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }

    .hero {
        padding: 1.5rem;
        border-radius: 15px;
        background: linear-gradient(120deg, #075985, #0f766e);
        color: white;
        margin-bottom: 1rem;
    }

    .hero h1 {
        color: white;
        margin-bottom: 0.3rem;
    }

    .hero p {
        color: white;
        font-size: 1.05rem;
    }

    .info-card {
        background: white;
        padding: 1rem;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        margin-bottom: 0.8rem;
    }

    .small-note {
        color: #64748b;
        font-size: 0.9rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------
# APPLICATION HEADER
# --------------------------------------------------

st.markdown(
    """
    <div class="hero">
        <h1>🦟 Dengue AI Guardian</h1>
        <p>
            Dengue awareness, symptom assessment, patient records,
            weather monitoring and prevention guidance.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------
# SIDEBAR NAVIGATION
# --------------------------------------------------

with st.sidebar:
    st.title("🦟 AI Guardian")
    st.caption("Dengue Awareness & Prevention")

    page = st.radio(
        "Navigation",
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

    if supabase is not None:
        st.success("Supabase connected")
    else:
        st.info("Using local SQLite database")

    st.caption("Educational prototype — not a medical diagnosis.")

# --------------------------------------------------
# DASHBOARD
# --------------------------------------------------

if page == "Dashboard":
    st.subheader("📊 Dashboard")

    records_df, database_name = load_records()

    total_records = len(records_df)

    if total_records:
        st.success(f"Patient records loaded from {database_name}.")
    else:
        st.info("No patient records have been saved yet.")

    col1, col2, col3 = st.columns(3)

    col1.metric("Saved Records", total_records)
    col2.metric("Data Source", database_name)
    col3.metric("Weather Data", "Open-Meteo")

    st.divider()

    st.subheader("🛡️ Dengue Prevention")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
            <div class="info-card">
                <h4>🦟 Prevent Mosquito Bites</h4>
                Use mosquito repellent, wear protective clothing,
                and use window screens or mosquito nets.
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class="info-card">
                <h4>💧 Remove Standing Water</h4>
                Empty and clean water containers regularly.
                Cover water storage containers properly.
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
            <div class="info-card">
                <h4>🩺 Seek Medical Advice</h4>
                Consult a healthcare professional if dengue is suspected.
                Do not rely on this application for diagnosis.
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class="info-card">
                <h4>🚨 Watch for Warning Signs</h4>
                Severe abdominal pain, persistent vomiting,
                bleeding, breathing difficulty or unusual drowsiness
                require urgent medical attention.
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.divider()
    st.caption(
        "This dashboard displays application records. "
        "It does not provide verified dengue case counts or a validated prediction."
    )

# --------------------------------------------------
# SYMPTOM ASSESSMENT
# --------------------------------------------------

elif page == "Symptom Assessment":
    st.subheader("🩺 Symptom Assessment")

    st.warning(
        "This form is an educational symptom checklist. "
        "It cannot diagnose dengue or estimate your clinical risk reliably."
    )

    with st.form("symptom_assessment_form"):
        patient_name = st.text_input(
            "Patient name (optional)",
            max_chars=100,
        )

        age = st.number_input(
            "Age",
            min_value=0,
            max_value=120,
            value=18,
        )

        temperature = st.number_input(
            "Body temperature (°C)",
            min_value=30.0,
            max_value=45.0,
            value=37.0,
            step=0.1,
        )

        st.markdown("**Select any symptoms present:**")

        col1, col2 = st.columns(2)

        with col1:
            headache = st.checkbox("Headache")
            rash = st.checkbox("Skin rash")
            vomiting = st.checkbox("Vomiting")

        with col2:
            joint_pain = st.checkbox("Joint or muscle pain")
            nausea = st.checkbox("Nausea")
            travel_history = st.checkbox(
                "Recent travel to an area with dengue transmission"
            )

        platelet_count_input = st.number_input(
            "Platelet count (optional; enter 0 if unknown)",
            min_value=0,
            max_value=1000000,
            value=0,
            step=1000,
        )

        warning_signs = st.checkbox(
            "Warning signs: severe abdominal pain, persistent vomiting, "
            "bleeding, breathing difficulty or unusual drowsiness"
        )

        submitted = st.form_submit_button(
            "Save Assessment",
            use_container_width=True,
        )

    if submitted:
        symptom_score = sum(
            [
                headache,
                rash,
                vomiting,
                joint_pain,
                nausea,
            ]
        )

        if warning_signs:
            assessment = "Urgent medical assessment needed"
        elif temperature >= 38.0:
            assessment = "Fever reported — seek medical advice"
        elif symptom_score > 0:
            assessment = "Symptoms reported — consult a healthcare professional"
        else:
            assessment = "No listed symptoms selected"

        record = {
            "record_date": datetime.now().isoformat(timespec="seconds"),
            "patient_name": patient_name.strip() or None,
            "age": int(age),
            "temperature": float(temperature),
            "headache": int(headache),
            "rash": int(rash),
            "vomiting": int(vomiting),
            "joint_pain": int(joint_pain),
            "nausea": int(nausea),
            "travel_history": int(travel_history),
            "platelet_count": (
                int(platelet_count_input)
                if platelet_count_input > 0
                else None
            ),
            "warning_signs": int(warning_signs),
            "symptom_score": int(symptom_score),
            "assessment": assessment,
        }

        success, storage = save_record(record)

        if success:
            st.success(f"Assessment saved successfully using {storage}.")

            st.write(f"**Symptoms reported:** {symptom_score} out of 5")
            st.write(f"**Recorded information:** {assessment}")

            if warning_signs:
                st.error(
                    "Seek emergency medical care now. Do not wait for "
                    "this application to assess your symptoms."
                )
            elif temperature >= 38.0:
                st.warning(
                    "Fever can have several causes. Please seek medical "
                    "advice, especially if dengue is possible."
                )
            elif symptom_score > 0:
                st.info(
                    "Symptoms alone cannot confirm or rule out dengue. "
                    "Consult a healthcare professional."
                )
        else:
            st.error(f"Could not save the record: {storage}")

# --------------------------------------------------
# PATIENT RECORDS
# --------------------------------------------------

elif page == "Patient Records":
    st.subheader("📋 Patient Records")

    if supabase is not None:
        st.write("Records are loaded from the Supabase database.")
    else:
        st.write(
            "Supabase is not configured yet; records are loaded "
            "from the app's local SQLite database."
        )

        if SUPABASE_ERROR:
            st.caption("Supabase connection is unavailable.")

    records_df, database_name = load_records()

    if records_df.empty:
        st.info("No patient records are available.")
    else:
        st.metric("Total Records", len(records_df))

        st.dataframe(
            records_df,
            use_container_width=True,
            hide_index=True,
        )

        csv_data = records_df.to_csv(index=False).encode("utf-8")

        st.download_button(
            "Download Records as CSV",
            data=csv_data,
            file_name="dengue_guardian_records.csv",
            mime="text/csv",
        )

        st.caption(
            "Use fictional demo records for exhibitions. "
            "Do not store identifiable real patient information "
            "without appropriate security and consent."
        )

# --------------------------------------------------
# WEATHER MONITOR
# --------------------------------------------------

elif page == "Weather Monitor":
    st.subheader("🌦️ Weather Monitor")

    st.write(
        "Fetches current weather observations from Open-Meteo "
        "for Bengaluru. Weather data cannot diagnose dengue."
    )

    if st.button("Fetch Bengaluru Weather", use_container_width=True):
        try:
            weather_url = (
                "https://api.open-meteo.com/v1/forecast"
            )

            params = {
                "latitude": 12.9716,
                "longitude": 77.5946,
                "current": (
                    "temperature_2m,relative_humidity_2m,"
                    "precipitation,rain,wind_speed_10m"
                ),
                "timezone": "Asia/Kolkata",
            }

            response = requests.get(
                weather_url,
                params=params,
                timeout=15,
            )
            response.raise_for_status()
            weather_data = response.json()
            current = weather_data.get("current", {})

            if not current:
                st.warning("No current weather data was returned.")
            else:
                st.success("Weather data fetched successfully.")

                col1, col2, col3 = st.columns(3)

                col1.metric(
                    "Temperature",
                    f"{current.get('temperature_2m', 'N/A')} °C",
                )

                col2.metric(
                    "Humidity",
                    f"{current.get('relative_humidity_2m', 'N/A')}%",
                )

                col3.metric(
                    "Precipitation",
                    f"{current.get('precipitation', 'N/A')} mm",
                )

                col1, col2 = st.columns(2)

                col1.metric(
                    "Rain",
                    f"{current.get('rain', 'N/A')} mm",
                )

                col2.metric(
                    "Wind Speed",
                    f"{current.get('wind_speed_10m', 'N/A')} km/h",
                )

                st.caption(
                    f"Observation time: {current.get('time', 'Unavailable')}"
                )

                st.json(current)

                st.info(
                    "Weather conditions are environmental observations, "
                    "not dengue case counts or an individual infection prediction."
                )

        except requests.RequestException as exc:
            st.error(f"Unable to fetch weather data: {exc}")

        except (ValueError, TypeError) as exc:
            st.error(f"Unexpected weather response: {exc}")

# --------------------------------------------------
# FOOD & PREVENTION
# --------------------------------------------------

elif page == "Food & Prevention":
    st.subheader("🥗 Food & Prevention")

    st.markdown("### General hydration and food guidance")

    st.markdown(
        """
        - Drink safe fluids regularly if you can tolerate them.
        - Oral rehydration solution may help when recommended or appropriate.
        - Eat balanced meals that are easy for you to tolerate.
        - Choose clean, safely prepared food.
        - Rest and follow advice from your healthcare professional.
        """
    )

    st.markdown("### Foods and drinks")

    st.markdown(
        """
        **Possible options:** water, oral rehydration solution when appropriate,
        soups, rice, cooked vegetables, fruit and other balanced foods you tolerate.

        **Be careful:** avoid unsafe or contaminated food and water.
        Do not force food or fluids if you are repeatedly vomiting or cannot
        keep fluids down; seek urgent medical advice.
        """
    )

    st.warning(
        "No food, juice or home remedy has been proven to cure dengue "
        "or reliably increase platelet counts. Follow clinical advice."
    )

    st.markdown("### Mosquito prevention")

    st.markdown(
        """
        - Use an appropriate mosquito repellent according to its label.
        - Wear long sleeves and trousers where practical.
        - Empty and scrub containers that collect standing water.
        - Cover stored water and maintain window screens.
        """
    )

    st.markdown("### Medicine safety")

    st.error(
        "If dengue is suspected, avoid aspirin and ibuprofen unless a "
        "qualified clinician specifically advises otherwise, because of "
        "bleeding risk. Ask a healthcare professional about appropriate "
        "fever treatment."
    )

# --------------------------------------------------
# GOVERNMENT INFORMATION
# --------------------------------------------------

elif page == "Government Information":
    st.subheader("🏥 Government Health Information")

    st.write(
        "Use official health sources for dengue prevention, symptoms "
        "and medical guidance."
    )

    st.markdown(
        """
        - [National Centre for Vector Borne Diseases Control (NCVBDC)](https://ncvbdc.mohfw.gov.in/)
        - [Ministry of Health and Family Welfare, India](https://mohfw.gov.in/)
        - [World Health Organization — Dengue](https://www.who.int/news-room/fact-sheets/detail/dengue-and-severe-dengue)
        """
    )

    st.info(
        "This prototype does not automatically connect to a government "
        "dengue case database. It does not display verified local outbreak "
        "statistics or hospital bed availability."
    )

    st.markdown("### When to seek emergency care")

    st.markdown(
        """
        Get urgent medical care for severe abdominal pain, persistent
        vomiting, bleeding, rapid or difficult breathing, fainting,
        confusion, unusual drowsiness, or inability to drink.
        Do not delay care while using this application.
        """
    )

# --------------------------------------------------
# ABOUT & SAFETY
# --------------------------------------------------

elif page == "About & Safety":
    st.subheader("ℹ️ About Dengue AI Guardian")

    st.markdown(
        """
        **Dengue AI Guardian** is an educational prototype demonstrating:

        - A symptom checklist and assessment form.
        - Patient record storage using SQLite.
        - Optional Supabase database integration.
        - Live weather retrieval through the Open-Meteo API.
        - General dengue prevention and food guidance.
        - CSV export of saved records.
        """
    )

    st.markdown("### Current limitations")

    st.markdown(
        """
        - This application does not contain a clinically validated
          dengue prediction model.
        - Symptom counts are not an AI prediction or a probability of dengue.
        - Weather observations do not establish infection or outbreak risk.
        - No CBC report analysis, LLM medical assistant, voice assistant,
          or live hospital availability system is implemented here.
        - Database availability depends on deployment configuration.
        """
    )

    st.error(
        "Do not use this application to diagnose dengue, interpret a "
        "blood report, choose treatment, or decide whether to delay care."
    )

    st.markdown("### Data privacy")

    st.markdown(
        """
        Use fictional records for demonstrations. SQLite data is stored
        in the application's local filesystem and may not persist across
        all hosted deployments or redeployments.

        Before storing real patient data, implement authentication,
        authorization, secure database policies, data minimization,
        retention controls and appropriate consent. Never expose a
        Supabase service-role key in application code or a public repository.
        """
    )

# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "Dengue AI Guardian | Educational prototype | "
    "Not a substitute for professional medical care"
)
