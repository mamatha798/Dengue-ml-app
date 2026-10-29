 























    st.subheader("Patient Records")
    if supabase is not None:
        st.write("Records are loaded from the Supabase database.")
    else:
        st.write("Supabase is not configured yet; records are loaded from the app's local SQLite database.")
        if SUPABASE_ERROR:
            st.warning("Supabase could not be initialized. Check the Secrets values and app logs.")
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
        "- Saves assessment entries to Supabase when configured; otherwise uses SQLite.\n"
        "- Adds missing columns when an older local SQLite database is opened.\n"
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
if supabase is None:
    st.sidebar.info("Database mode: local SQLite. Add SUPABASE_URL and SUPABASE_KEY in Streamlit Secrets to enable Supabase.")
else:
    st.sidebar.success("Database mode: Supabase")

You're using the free version of ChatGPT. Upgrade for advanced models, better memory, and higher-quality image creation.


⋮⋮⋮⋮
