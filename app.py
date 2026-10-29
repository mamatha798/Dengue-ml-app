
import streamlit as st
import sqlite3
import requests
from datetime import datetime
from pathlib import Path

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Dengue AI Guardian",
    page_icon="🦟",
    layout="wide",
    initial_sidebar_state="expanded"
)

DB_PATH = Path(__file__).with_name("dengue_guardian.db")

# ---------------- DESIGN / CSS ----------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

[data-testid="stAppViewContainer"] {
    background-color: #F4F7FB;
}

[data-testid="stHeader"] {
    background-color: #F4F7FB;
}

[data-testid="stSidebar"] {
    background-color: #102A43;
}

[data-testid="stSidebar"] > div {
    background-color: #102A43;
}

[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
    color: #FFFFFF !important;
}

/* FIX: Make main-page field labels visible */
[data-testid="stMain"] label,
[data-testid="stMain"] [data-testid="stWidgetLabel"],
[data-testid="stMain"] [data-testid="stWidgetLabel"] p,
[data-testid="stMain"] [data-testid="stMarkdownContainer"] p {
    color: #17324D !important;
    -webkit-text-fill-color: #17324D !important;
    font-weight: 600 !important;
    opacity: 1 !important;
}

/* Dropdown text and background */
[data-testid="stMain"] [data-baseweb="select"] > div {
    background-color: #FFFFFF !important;
    border-color: #CBD5E1 !important;
}

[data-testid="stMain"] [data-baseweb="select"] * {
    color: #17324D !important;
    -webkit-text-fill-color: #17324D !important;
}

[data-testid="stMain"] input {
    color: #17324D !important;
    -webkit-text-fill-color: #17324D !important;
    background-color: #FFFFFF !important;
}

/* Main headings */
h1, h2, h3 {
    color: #102A43;
}

.hero {
    background: linear-gradient(120deg, #102A43, #087E8B);
    padding: 28px;
    border-radius: 18px;
    color: white;
    margin-bottom: 22px;
}

.hero h1, .hero p {
    color: white !important;
}

.metric-card {
    background: white;
    border: 1px solid #E1E8F0;
    padding: 20px;
    border-radius: 14px;
    margin-bottom: 10px;
}

.metric-label {
    color: #526579;
    font-size: 14px;
}

.metric-value {
    color: #102A43;
    font-size: 25px;
    font-weight: 800;
}

.info-card {
    background: white;
    border-left: 4px solid #087E8B;
    border-radius: 10px;
    padding: 16px;
    margin: 10px 0;
    color: #17324D;
}

div.stButton > button {
    background-color: #087E8B;
    color: white !important;
    border: none;
    border-radius: 9px;
    padding: 10px 18px;
    font-weight: 700;
}

div.stButton > button:hover {
    background-color: #066773;
    color: white !important;
}

div[data-testid="stAlert"] {
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)


# ---------------- DATABASE ----------------
def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    with get_connection() as conn:
        conn.execute("""
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
                warning_signs TEXT,
                symptom_score INTEGER
            )
        """)


initialize_database()


# ---------------- WEATHER ----------------
@st.cache_data(ttl=900, show_spinner=False)
def get_weather():
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": 12.9716,
        "longitude": 77.5946,
        "current": "temperature_2m,relative_humidity_2m,precipitation",
        "timezone": "Asia/Kolkata"
    }

    try:
        response = requests.get(url, params=params, timeout=8)
        response.raise_for_status()
        data = response.json()
        current = data.get("current", {})
        return {
            "temperature": current.get("temperature_2m"),
            "humidity": current.get("relative_humidity_2m"),
            "precipitation": current.get("precipitation"),
            "time": current.get("time")
        }
    except (requests.RequestException, ValueError):
        return None


# ---------------- SIDEBAR ----------------
st.sidebar.markdown("# 🦟 Dengue")
st.sidebar.markdown("### AI Guardian")
st.sidebar.caption("Awareness • Assessment • Safety")
st.sidebar.divider()

page = st.sidebar.radio(
    "NAVIGATION",
    [
        "Dashboard",
        "Symptom Assessment",
        "Patient Records",
        "Weather Monitor",
        "Food & Prevention",
        "Government Information",
        "About & Safety"
    ]
)

st.sidebar.divider()
st.sidebar.caption("Educational support only — not a medical diagnosis.")


# ---------------- HEADER ----------------
st.markdown("""
<div class="hero">
    <h1>🦟 Dengue AI Guardian</h1>
    <p>Community awareness, symptom tracking and prevention support.</p>
</div>
""", unsafe_allow_html=True)


# ---------------- DASHBOARD ----------------
if page == "Dashboard":
    st.subheader("Dashboard")
    st.write("Monitor saved assessments, current weather and dengue prevention guidance.")

    with get_connection() as conn:
        total_records = conn.execute(
            "SELECT COUNT(*) FROM patient_records"
        ).fetchone()[0]

        today = datetime.now().strftime("%Y-%m-%d")
        today_records = conn.execute(
            "SELECT COUNT(*) FROM patient_records WHERE record_date LIKE ?",
            (today + "%",)
        ).fetchone()[0]

        warning_records = conn.execute("""
            SELECT COUNT(*) FROM patient_records
            WHERE warning_signs != 'None reported'
        """).fetchone()[0]

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">Saved assessments</div>'
            f'<div class="metric-value">{total_records}</div></div>',
            unsafe_allow_html=True
        )

    with c2:
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">Assessments today</div>'
            f'<div class="metric-value">{today_records}</div></div>',
            unsafe_allow_html=True
        )

    with c3:
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">Records with warning signs</div>'
            f'<div class="metric-value">{warning_records}</div></div>',
            unsafe_allow_html=True
        )

    st.subheader("Current Bengaluru weather")
    weather = get_weather()

    if weather:
        w1, w2, w3 = st.columns(3)

        with w1:
            st.metric("Temperature", f"{weather['temperature']} °C"
                      if weather["temperature"] is not None else "Unavailable")

        with w2:
            st.metric("Relative humidity", f"{weather['humidity']}%"
                      if weather["humidity"] is not None else "Unavailable")

        with w3:
            st.metric("Precipitation", f"{weather['precipitation']} mm"
                      if weather["precipitation"] is not None else "Unavailable")

        st.caption(f"Weather observation time: {weather['time']}")
    else:
        st.warning("Weather service is temporarily unavailable.")

    st.markdown("""
    <div class="info-card">
    <b>Important:</b> Weather conditions alone cannot predict whether a person has dengue.
    Symptoms and laboratory tests need assessment by a qualified healthcare professional.
    </div>
    """, unsafe_allow_html=True)

    st.subheader("Quick actions")
    q1, q2 = st.columns(2)

    with q1:
        if st.button("Open Symptom Assessment", use_container_width=True):
            st.info("Choose 'Symptom Assessment' from the navigation menu.")

    with q2:
        if st.button("View Patient Records", use_container_width=True):
            st.info("Choose 'Patient Records' from the navigation menu.")


# ---------------- SYMPTOM ASSESSMENT ----------------
elif page == "Symptom Assessment":
    st.subheader("Symptom Assessment")
    st.write("Enter the information below. Fields are labelled individually for clarity.")

    st.warning(
        "This form records symptoms for awareness and tracking. "
        "It does not calculate a validated dengue probability or diagnose dengue."
    )

    with st.form("dengue_assessment_form"):
        st.markdown("### Patient Information")

        col1, col2 = st.columns(2)

        with col1:
            temperature = st.number_input(
                "Body temperature (°C)",
                min_value=34.0,
                max_value=43.0,
                value=37.0,
                step=0.1,
                help="Enter the measured temperature in degrees Celsius."
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
            joint_pain = st.selectbox(
                "Joint or muscle pain",
                ["No", "Mild", "Severe"]
            )

            nausea = st.selectbox(
                "Nausea",
                ["No", "Yes"]
            )

            travel_history = st.selectbox(
                "Recent travel to an area with reported dengue",
                ["Unknown", "No", "Yes"]
            )

            platelet_count = st.number_input(
                "Platelet count (if known, cells/µL)",
                min_value=0,
                max_value=1000000,
                value=0,
                step=1000,
                help="Enter 0 if you do not have a platelet report."
            )

        st.markdown("### Warning Signs")
        st.caption("Select any warning signs currently present.")

        warning_sign_options = [
            "Severe abdominal pain",
            "Repeated or persistent vomiting",
            "Bleeding from nose or gums",
            "Blood in vomit or stool",
            "Difficulty breathing",
            "Unusual drowsiness, confusion or restlessness",
            "Cold, pale or clammy skin"
        ]

        warning_signs = st.multiselect(
            "Warning signs",
            warning_sign_options,
            default=[],
            help="These signs can indicate severe illness and require urgent medical assessment."
        )

        consent = st.checkbox(
            "I understand this is an educational tool and not a medical diagnosis."
        )

        submitted = st.form_submit_button(
            "Save Assessment",
            use_container_width=True
        )

    if submitted:
        if not consent:
            st.error("Please confirm the educational-use notice before saving.")
        else:
            warning_text = ", ".join(warning_signs) if warning_signs else "None reported"

            # A simple count for record tracking only; NOT a dengue prediction.
            symptom_score = sum([
                temperature >= 38.0,
                headache != "No",
                rash == "Yes",
                vomiting == "Yes",
                joint_pain != "No",
                nausea == "Yes"
            ])

            try:
                with get_connection() as conn:
                    conn.execute("""
                        INSERT INTO patient_records (
                            record_date, temperature, headache, rash, vomiting,
                            joint_pain, nausea, travel_history, platelet_count,
                            warning_signs, symptom_score
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        datetime.now().isoformat(timespec="seconds"),
                        temperature,
                        headache,
                        rash,
                        vomiting,
                        joint_pain,
                        nausea,
                        travel_history,
                        platelet_count if platelet_count > 0 else None,
                        warning_text,
                        symptom_score
                    ))

                st.success("Assessment saved successfully.")

                if warning_signs:
                    st.error(
                        "URGENT: One or more warning signs were selected. "
                        "Seek urgent medical care now. Do not wait for this app "
                        "or a platelet count to decide whether to get help."
                    )
                elif temperature >= 38.0:
                    st.warning(
                        "A fever was entered. Contact a healthcare professional "
                        "for advice, especially if fever persists or dengue is suspected."
                    )
                else:
                    st.info(
                        "Your information was saved. This app cannot rule out dengue. "
                        "Seek medical advice if symptoms develop or worsen."
                    )

                if platelet_count > 0 and platelet_count < 100000:
                    st.warning(
                        "The entered platelet count is below 100,000 cells/µL. "
                        "Discuss the result promptly with a healthcare professional. "
                        "A platelet count alone cannot diagnose or exclude dengue."
                    )

                st.caption(
                    f"Symptom items recorded: {symptom_score}. "
                    "This is a simple count, not a risk score or ML prediction."
                )

            except sqlite3.Error as error:
                st.error(f"Could not save the assessment: {error}")


# ---------------- PATIENT RECORDS ----------------
elif page == "Patient Records":
    st.subheader("Patient Records")
    st.write("Assessments saved in this app's SQLite database.")

    with get_connection() as conn:
        rows = conn.execute("""
            SELECT id, record_date, temperature, headache, rash, vomiting,
                   joint_pain, nausea, travel_history, platelet_count,
                   warning_signs, symptom_score
            FROM patient_records
            ORDER BY id DESC
        """).fetchall()

    if rows:
        records = [dict(row) for row in rows]
        st.dataframe(records, use_container_width=True, hide_index=True)

        csv_data = st.dataframe if False else None
        import csv
        import io

        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=records[0].keys())
        writer.writeheader()
        writer.writerows(records)

        st.download_button(
            "Download records as CSV",
            data=output.getvalue(),
            file_name="dengue_guardian_records.csv",
            mime="text/csv"
        )

        st.caption(
            "Privacy note: these records are stored in the app's SQLite database. "
            "Avoid entering identifiable personal information in a public demo."
        )
    else:
        st.info("No saved assessments yet. Complete the Symptom Assessment form first.")


# ---------------- WEATHER MONITOR ----------------
elif page == "Weather Monitor":
    st.subheader("Bengaluru Weather Monitor")
    st.write("Current weather data retrieved from Open-Meteo.")

    if st.button("Refresh weather"):
        get_weather.clear()

    weather = get_weather()

    if weather:
        c1, c2, c3 = st.columns(3)

        with c1:
            st.metric(
                "Temperature",
                f"{weather['temperature']} °C"
                if weather["temperature"] is not None else "Unavailable"
            )

        with c2:
            st.metric(
                "Humidity",
                f"{weather['humidity']}%"
                if weather["humidity"] is not None else "Unavailable"
            )

        with c3:
            st.metric(
                "Precipitation",
                f"{weather['precipitation']} mm"
                if weather["precipitation"] is not None else "Unavailable"
            )

        st.caption(f"Observation time: {weather['time']}")
    else:
        st.error("Could not retrieve live weather right now. Please try again later.")

    st.markdown("""
    <div class="info-card">
    Weather information is environmental context only. It is not patient data,
    and it cannot confirm or predict an individual dengue infection.
    </div>
    """, unsafe_allow_html=True)


# ---------------- FOOD & PREVENTION ----------------
elif page == "Food & Prevention":
    st.subheader("Food, Hydration & Prevention")

    st.markdown("### During a fever or suspected dengue")

    st.markdown("""
    - Drink fluids regularly, such as water or oral rehydration solution (ORS),
      if you can drink safely.
    - Eat small, balanced meals that you tolerate, such as rice, dal, soup,
      cooked vegetables and fruit.
    - Follow the advice of your treating healthcare professional.
    - Do not rely on papaya leaf juice, special foods or supplements as a cure.
    """)

    st.markdown("### Avoid mosquito bites")

    st.markdown("""
    - Use an appropriate mosquito repellent according to its label.
    - Wear clothing that covers arms and legs where practical.
    - Use window screens or mosquito nets.
    - Empty, cover or clean containers where water collects at least weekly.
    - Seek medical advice if you have fever and suspect dengue.
    """)

    st.warning(
        "If dengue is suspected, do not self-medicate with aspirin or ibuprofen "
        "because they can increase bleeding risk. Ask a healthcare professional "
        "which medicine is appropriate for you."
    )

    st.error(
        "Seek urgent medical care for severe abdominal pain, persistent vomiting, "
        "bleeding, breathing difficulty, confusion, or cold and clammy skin."
    )


# ---------------- GOVERNMENT INFORMATION ----------------
elif page == "Government Information":
    st.subheader("Government Information & Resources")

    st.markdown("""
    Use trusted public-health sources for current dengue guidance:

    - **National Centre for Vector Borne Diseases Control (NCVBDC):**
      https://ncvbdc.mohfw.gov.in/
    - **World Health Organization — Dengue:**
      https://www.who.int/news-room/fact-sheets/detail/dengue-and-severe-dengue
    - **Open-Meteo weather service:**
      https://open-meteo.com/
    """)

    st.info(
        "This page provides links to public resources. It does not automatically "
        "fetch official dengue case statistics, and no live case count is claimed."
    )


# ---------------- ABOUT & SAFETY ----------------
elif page == "About & Safety":
    st.subheader("About Dengue AI Guardian")

    st.markdown("""
    **Purpose**

    Dengue AI Guardian is an educational prototype for symptom recording,
    environmental context, prevention awareness and basic record management.

    **Current capabilities**
    - Symptom assessment form
    - SQLite storage for assessment records
    - Current weather data from Open-Meteo
    - CSV export of saved records
    - Prevention and public-health links

    **Current limitations**
    - No clinically validated dengue prediction model is implemented.
    - Symptom counts are not a diagnosis or calibrated risk estimate.
    - Weather data does not establish a patient's infection status.
    - The app does not replace a doctor, blood tests or emergency care.
    - SQLite data on a hosted service may not be permanent across restarts
      or redeployments, depending on the hosting environment.
    """)

    st.error(
        "Emergency warning: severe abdominal pain, persistent vomiting, bleeding, "
        "difficulty breathing, confusion or cold/clammy skin require urgent medical care."
    )

    st.markdown(
        "For suspected dengue, consult a qualified healthcare professional. "
        "Do not delay care because of a result shown by this app."
    )


# ---------------- FOOTER ----------------
st.divider()
st.caption(
    "Dengue AI Guardian • Educational prototype • "
    "Not a substitute for professional medical advice."
)
