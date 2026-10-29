























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

from supabase import create_client

SUPABASE_URL = st.secrets.get("SUPABASE_URL", "")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "")
supabase = None
SUPABASE_ERROR = None

if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as exc:
        SUPABASE_ERROR = str(exc)

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
    /* Fix blurry weather metrics and values */
[data-testid="stMetric"] {
    background-color: #ffffff !important;
    border: 1px solid #dce7ee !important;
    border-radius: 14px !important;
    padding: 18px !important;
    opacity: 1 !important;
    filter: none !important;
}

[data-testid="stMetricLabel"],
[data-testid="stMetricLabel"] p {
    color: #17324d !important;
    opacity: 1 !important;
    filter: none !important;
    font-size: 15px !important;
    font-weight: 700 !important;
}

[data-testid="stMetricValue"],
[data-testid="stMetricValue"] div,
[data-testid="stMetricValue"] p {
    color: #087e8b !important;
    opacity: 1 !important;
    filter: none !important;
    font-size: 30px !important;
    font-weight: 800 !important;
    -webkit-text-fill-color: #087e8b !important;
}
You're using the free version of ChatGPT. Upgrade for advanced models, better memory, and higher-quality image creation.


⋮⋮⋮⋮
