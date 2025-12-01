import streamlit as st
import sqlite3
import matplotlib

def create_table():
    conn = sqlite3.connect('dengue_data.db')
    cur = conn.cursor()
    cur.execute('''
    CREATE TABLE IF NOT EXISTS dengue_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fever REAL,
        headache TEXT,
        rash TEXT,
        vomiting TEXT,
        platelet_count INTEGER,
        joint_pain TEXT,
        nausea TEXT,
        travel_history TEXT,
        risk_level TEXT
    )
    ''')
    conn.commit()
    conn.close()

create_table()  # Call it

# ============================
# APP TITLE
# ============================
st.title("Dengue Prediction App")

# ----- BACK LINK -----
st.markdown('[🔙 Back to Website](https://github.com/mamatha798/Dengueprediction)')

st.write("Enter the details below to check dengue possibility.")

# ============================
# Function to calculate risk based on input
# ============================
def calculate_risk(fever, headache, rash, vomiting, platelets, joint_pain, nausea, travel_history):
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
    
    if risk_score >= 6:
        return "High Risk", "red"
    elif risk_score >= 3:
        return "Moderate Risk", "orange"
    else:
        return "Low Risk", "green"

# ============================
# Function to save data into the database
# ============================
def save_data(fever, headache, rash, vomiting, platelets, joint_pain, nausea, travel_history, risk_level):
    # Connect to the SQLite database
    conn = sqlite3.connect('dengue_data.db')
    cur = conn.cursor()

    # Insert the data into the table
    cur.execute('''
    INSERT INTO dengue_records (fever, headache, rash, vomiting, platelet_count, joint_pain, nausea, travel_history, risk_level)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (fever, headache, rash, vomiting, platelets, joint_pain, nausea, travel_history, risk_level))

    # Commit changes and close the connection
    conn.commit()
    conn.close()

# ============================
# Collect Data for Multiple Records
# ============================
with st.form(key='dengue_form'):
    st.subheader("Enter a person's data:")

    fever = st.number_input("Fever (°C)", min_value=35.0, max_value=42.0, step=0.1)
    headache = st.selectbox("Headache", ["No", "Mild", "Severe"])
    rash = st.selectbox("Skin Rash", ["No", "Yes"])
    vomiting = st.selectbox("Vomiting", ["No", "Yes"])
    platelets = st.number_input("Platelet Count", min_value=10000, max_value=500000, step=1000)
    joint_pain = st.selectbox("Joint/Muscle Pain", ["No", "Yes"])
    nausea = st.selectbox("Nausea", ["No", "Yes"])
    travel_history = st.selectbox("Recent Travel to Dengue-prone Area", ["No", "Yes"])

    submit_button = st.form_submit_button("Submit Record")

    if submit_button:
        # Calculate risk level for the entered data
        risk_level, color = calculate_risk(fever, headache, rash, vomiting, platelets, joint_pain, nausea, travel_history)
        
        # Save the record in the database
        save_data(fever, headache, rash, vomiting, platelets, joint_pain, nausea, travel_history, risk_level)
        
        # Display the result
        st.markdown(f"**Risk Level**: {risk_level}")
        st.markdown(f"Risk Level color: {color}")

        # Plot the risk level as a bar chart
        fig, ax = plt.subplots()
        ax.bar(risk_level, 1, color=color)
        ax.set_ylabel('Risk')
        ax.set_title('Dengue Risk Level')
        ax.set_ylim(0, 2)  # Only display from 0 to 2 for better readability
        
        # Display the plot
        st.pyplot(fig)

# ============================
# Show all records
# ============================
st.subheader("View All Submitted Records")

# Function to fetch data from the database
def fetch_data():
    conn = sqlite3.connect('dengue_data.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM dengue_records")
    rows = cur.fetchall()
    conn.close()
    return rows

# Display all records in the database
records = fetch_data()
if records:
    st.write("Here are all the records with risk levels:")
    st.dataframe(records)
else:
    st.write("No records found yet.")
