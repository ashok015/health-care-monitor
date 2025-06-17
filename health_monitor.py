import streamlit as st
import pandas as pd
import random
import smtplib
from email.message import EmailMessage
from datetime import datetime

# -------------------------
# Generate Random Vitals
# -------------------------
def generate_sample_data():
    return {
        "Heart Rate": random.randint(55, 135),
        "BP Systolic": random.randint(95, 175),
        "BP Diastolic": random.randint(65, 105),
        "Temperature": round(random.uniform(36.2, 39.8), 1),
        "Glucose": random.randint(80, 230),
        "SpO2": random.randint(88, 100)
    }

# -------------------------
# Evaluate health status
# -------------------------
def evaluate_status(vitals):
    issues = 0
    if vitals['Heart Rate'] < 60 or vitals['Heart Rate'] > 120:
        issues += 1
    if vitals['BP Systolic'] > 140 or vitals['BP Diastolic'] > 90:
        issues += 1
    if vitals['Temperature'] > 38.5:
        issues += 1
    if vitals['Glucose'] > 180:
        issues += 1
    if vitals['SpO2'] < 92:
        issues += 1

    if issues == 0:
        return "Normal"
    elif issues <= 2:
        return "Warning"
    else:
        return "Critical"

# -------------------------
# Send Email Alert
# -------------------------
def send_email_alert(vitals, receiver_email, user_name, medical_info):
    EMAIL_ADDRESS = st.secrets["credentials"]["EMAIL_ADDRESS"]
    EMAIL_PASSWORD = st.secrets["credentials"]["EMAIL_PASSWORD"]

    msg = EmailMessage()
    msg['Subject'] = "Critical Health Alert"
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = receiver_email

    content = f"""
    Critical health alert triggered.

    Name: {user_name}
    Email: {receiver_email}
    Medical History: {medical_info}

    Vitals:
    - Heart Rate: {vitals['Heart Rate']} bpm
    - Blood Pressure: {vitals['BP Systolic']}/{vitals['BP Diastolic']}
    - Temperature: {vitals['Temperature']} °C
    - Glucose: {vitals['Glucose']} mg/dL
    - SpO2: {vitals['SpO2']} %

    Please consult a doctor immediately.
    """
    msg.set_content(content)

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        st.error(f"Failed to send email: {e}")
        return False

# -------------------------
# Streamlit App
# -------------------------
st.set_page_config(page_title="Health Monitor", layout="wide")
st.title("Health Monitor System")

# -------------------------
# Step 1: Get User Info
# -------------------------
if 'user_registered' not in st.session_state:
    with st.form("user_form"):
        st.subheader("User Details")
        name = st.text_input("Full Name")
        email = st.text_input("Email Address (to receive alerts)")
        medical = st.text_area("Medical History (e.g., Diabetes, Hypertension, etc.)")
        submit = st.form_submit_button("Save & Start Monitoring")

        if submit and name and email:
            st.session_state.user_name = name
            st.session_state.user_email = email
            st.session_state.user_medical = medical
            st.session_state.user_registered = True
            st.success("Details saved! You can now start monitoring.")
        elif submit:
            st.warning("Please fill all fields.")

# -------------------------
# Step 2: Start Monitoring
# -------------------------
if st.session_state.get('user_registered'):
    if 'record_log' not in st.session_state:
        st.session_state['record_log'] = []

    if st.button("Check Health Now"):
        vitals = generate_sample_data()
        status = evaluate_status(vitals)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        record = {
            "Timestamp": timestamp,
            **vitals,
            "Status": status
        }
        st.session_state['record_log'].append(record)

        st.subheader(f"Health Status: {status}")
        st.dataframe(pd.DataFrame([record]))

        if status == "Critical":
            sent = send_email_alert(vitals, st.session_state.user_email,
                                    st.session_state.user_name, st.session_state.user_medical)
            if sent:
                st.error("Alert email sent to the user.")
            else:
                st.warning("Email sending failed.")

    if st.session_state['record_log']:
        st.subheader("Monitoring History")
        df = pd.DataFrame(st.session_state['record_log'])
        st.dataframe(df)
        st.download_button("Download Report", df.to_csv(index=False), "health_log.csv")
