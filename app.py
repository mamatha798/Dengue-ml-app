import streamlit as st

# ============================
# APP TITLE
# ============================
st.title("Dengue Prediction App")

# ----- BACK LINK -----
st.markdown('[🔙 Back to Website](https://github.com/mamatha798/Dengueprediction)')

st.write("Enter the details below to check dengue possibility.")

# ============================
# USER INPUTS
# ============================
fever = st.number_input("Fever (°C)", min_value=35.0, max_value=42.0, step=0.1)
headache = st.selectbox("Headache", ["No", "Mild", "Severe"])
rash = st.selectbox("Skin Rash", ["No", "Yes"])
vomiting = st.selectbox("Vomiting", ["No", "Yes"])
platelets = st.number_input("Platelet Count", min_value=10000, max_value=500000, step=1000)
joint_pain = st.selectbox("Joint/Muscle Pain", ["No", "Yes"])
nausea = st.selectbox("Nausea", ["No", "Yes"])
travel_history = st.selectbox("Recent Travel to Dengue-prone Area", ["No", "Yes"])

# ============================
# PREDICTION LOGIC
# ============================
if st.button("Predict"):
    # ----- SIMPLE RISK LOGIC -----
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

    # ----- RISK LEVEL -----
    if risk_score >= 6:
        risk_level = "High Risk"
        st.error("High Risk of Dengue! Please consult a doctor immediately.")
    elif risk_score >= 3:
        risk_level = "Moderate Risk"
        st.warning("Moderate Risk of Dengue. Take precautions and monitor symptoms.")
    else:
        risk_level = "Low Risk"
        st.success("Low Risk of Dengue. Continue preventive measures.")

# ----- FOOTER -----
st.markdown("---")
st.info("ℹ️ This is a demo prediction app. Real Machine Learning model integration will be added soon.")
