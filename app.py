import streamlit as st
import pandas as pd

# ----- APP TITLE -----
st.title("Dengue Prediction App")

# ----- BACK LINK -----
st.markdown('[🔙 Back to Website](https://github.com/mamatha798/Dengueprediction)')

st.write("Enter the details below to check dengue possibility.")

# ----- USER INPUTS -----
fever = st.number_input("Fever (°C)", min_value=35.0, max_value=42.0, step=0.1)
headache = st.selectbox("Headache", ["No", "Mild", "Severe"])
rash = st.selectbox("Skin Rash", ["No", "Yes"])
vomiting = st.selectbox("Vomiting", ["No", "Yes"])
platelets = st.number_input("Platelet Count", min_value=10000, max_value=500000, step=1000)
joint_pain = st.selectbox("Joint/Muscle Pain", ["No", "Yes"])
nausea = st.selectbox("Nausea", ["No", "Yes"])
travel_history = st.selectbox("Recent Travel to Dengue-prone Area", ["No", "Yes"])

# ----- PREDICTION BUTTON -----
if st.button("Predict"):
    # ----- DUMMY LOGIC -----
    risk_score = 0
    if fever > 38: risk_score += 2
    if headache == "Severe": risk_score += 2
    elif headache == "Mild": risk_score += 1
    if rash == "Yes": risk_score += 1
    if vomiting == "Yes": risk_score += 1
    if platelets < 150000: risk_score += 2
    if joint_pain == "Yes": risk_score += 1
    if nausea == "Yes": risk_score += 1
    if travel_history == "Yes": risk_score += 1

    # ----- DETERMINE RISK LEVEL -----
    if risk_score >= 6:
        risk_level = "High Risk"
        st.error("High Risk of Dengue! Please consult a doctor immediately.")
        bar_color = 'red'
    elif risk_score >= 3:
        risk_level = "Moderate Risk"
        st.warning("Moderate Risk of Dengue. Take precautions and monitor symptoms.")
        bar_color = 'orange'
    else:
        risk_level = "Low Risk"
        st.success("Low Risk of Dengue. Continue preventive measures.")
        bar_color = 'green'

    # ----- SHOW RISK LEVEL CHART -----
    st.subheader("Risk Factor Contribution")
    data = pd.DataFrame({
        'Risk Factor': ['Fever', 'Headache', 'Rash', 'Vomiting', 'Platelets', 'Joint Pain', 'Nausea', 'Travel History'],
        'Score': [
            2 if fever > 38 else 0,
            2 if headache == "Severe" else 1 if headache == "Mild" else 0,
            1 if rash == "Yes" else 0,
            1 if vomiting == "Yes" else 0,
            2 if platelets < 150000 else 0,
            1 if joint_pain == "Yes" else 0,
            1 if nausea == "Yes" else 0,
            1 if travel_history == "Yes" else 0
        ]
    })
    
    # Color-coded chart
    import matplotlib.pyplot as plt
    plt.figure(figsize=(8,4))
    colors = ['red' if val > 1 else 'orange' if val == 1 else 'green' for val in data['Score']]
    plt.bar(data['Risk Factor'], data['Score'], color=colors)
    plt.ylabel("Score Contribution")
    plt.title(f"Overall Risk Level: {risk_level}")
    plt.xticks(rotation=45)
    plt.ylim(0, 3)
    st.pyplot(plt)

# ----- FOOTER INFO -----
st.markdown("---")
st.info("ℹ️ This is a demo prediction app. Real ML model integration will be added soon.")
