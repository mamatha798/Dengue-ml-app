import streamlit as st

st.title("Dengue Prediction App")
st.write("Enter the details below to check dengue possibility.")

fever = st.number_input("Fever (°C)", min_value=90.0, max_value=110.0, step=0.1)
headache = st.selectbox("Headache", ["No", "Mild", "Severe"])
rash = st.selectbox("Skin Rash", ["No", "Yes"])
vomiting = st.selectbox("Vomiting", ["No", "Yes"])
platelets = st.number_input("Platelet Count", min_value=10000, max_value=500000, step=1000)

if st.button("Predict"):
    st.success("This is a demo prediction. ML model will be added soon!")
