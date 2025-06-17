# ============================================
# Health Monitor App (Final Polished Version)
# ============================================

import streamlit as st
import smtplib
from email.message import EmailMessage

# --------------------------------------------
# Configuration: Read from Streamlit secrets
# --------------------------------------------
EMAIL_ADDRESS = st.secrets["credentials"]["email"]
EMAIL_PASSWORD = st.secrets["credentials"]["password"]

# --------------------------------------------
# Email alert function
# --------------------------------------------
def send_email_alert(vitals, receiver_email, health_status):
    try:
        msg = EmailMessage()
        msg['Subject'] = 'Health Report Summary'
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = receiver_email

        table = f"""
        | Vital Sign       | Value       |
        |------------------|-------------|
        | Heart Rate       | {vitals['Heart Rate']} bpm |
        | BP Systolic      | {vitals['BP Systolic']} mmHg |
        | BP Diastolic     | {vitals['BP Diastolic']} mmHg |
        | Temperature      | {vitals['Temperature']} °C |
        | Glucose Level    | {vitals['Glucose']} mg/dL |
        | SpO2             | {vitals['SpO2']}% |
        """

        content = f"""
Hello,

This is your latest health report from the Health Monitor App.

Health Status: {health_status}

{table}

Thank you,
Health Monitor System
        """

        msg.set_content(content)

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)

        return True
    except Exception as e:
        st.warning("Could not send email: " + str(e))
        return False

# --------------------------------------------
# Health evaluation function
# --------------------------------------------
def evaluate_health(vitals):
    issues = 0
    if vitals['Heart Rate'] < 60 or vitals['Heart Rate'] > 100:
        issues += 1
    if vitals['BP Systolic'] > 130 or vitals['BP Diastolic'] > 85:
        issues += 1
    if vitals['Temperature'] > 38 or vitals['Temperature'] < 36:
        issues += 1
    if vitals['Glucose'] > 140:
        issues += 1
    if vitals['SpO2'] < 94:
        issues += 1

    if issues == 0:
        return "Normal"
    elif issues <= 2:
        return "Warning"
    else:
        return "Critical"

# --------------------------------------------
# Streamlit App Configuration
# --------------------------------------------
st.set_page_config(page_title="Health Monitor App", layout="centered")

# --------------------------------------------
# Session State Initialization
# --------------------------------------------
if 'page' not in st.session_state:
    st.session_state.page = 1

if 'user_name' not in st.session_state:
    st.session_state.user_name = ""

if 'user_email' not in st.session_state:
    st.session_state.user_email = ""

if 'vitals' not in st.session_state:
    st.session_state.vitals = {
        "Heart Rate": 75,
        "BP Systolic": 120,
        "BP Diastolic": 80,
        "Temperature": 37,
        "Glucose": 100,
        "SpO2": 98
    }

# --------------------------------------------
# PAGE 1 – USER INFO
# --------------------------------------------
if st.session_state.page == 1:
    st.title("Welcome to the Health Monitor App")
    st.write("Please provide your information to begin.")

    st.session_state.user_name = st.text_input("Full Name")
    st.session_state.user_email = st.text_input("Your Email Address")

    if st.button("Next"):
        if st.session_state.user_email and st.session_state.user_name:
            st.session_state.page = 2
        else:
            st.warning("Both fields are required to proceed.")

# --------------------------------------------
# PAGE 2 – VITAL FORM
# --------------------------------------------
elif st.session_state.page == 2:
    st.title("Medical Report Entry")
    st.write("Please input your current vital signs.")

    vitals = st.session_state.vitals

    vitals['Heart Rate'] = int(st.number_input("Heart Rate (bpm)", min_value=30, max_value=200, value=vitals['Heart Rate']))
    vitals['BP Systolic'] = int(st.number_input("Systolic Blood Pressure", min_value=80, max_value=200, value=vitals['BP Systolic']))
    vitals['BP Diastolic'] = int(st.number_input("Diastolic Blood Pressure", min_value=50, max_value=130, value=vitals['BP Diastolic']))
    vitals['Temperature'] = int(st.number_input("Body Temperature (°C)", min_value=34, max_value=42, value=vitals['Temperature']))
    vitals['Glucose'] = int(st.number_input("Blood Glucose (mg/dL)", min_value=50, max_value=300, value=vitals['Glucose']))
    vitals['SpO2'] = int(st.number_input("Oxygen Saturation (SpO2 %)", min_value=80, max_value=100, value=vitals['SpO2']))

    if st.button("Generate Report"):
        st.session_state.page = 3

# --------------------------------------------
# PAGE 3 – REPORT
# --------------------------------------------
elif st.session_state.page == 3:
    st.title("Your Health Summary")

    vitals = st.session_state.vitals
    status = evaluate_health(vitals)

    st.subheader(f"Patient: {st.session_state.user_name}")
    st.write("### Vital Signs")
    st.table({
        "Vital": ["Heart Rate", "BP Systolic", "BP Diastolic", "Temperature", "Glucose", "SpO2"],
        "Value": [
            f"{vitals['Heart Rate']} bpm",
            f"{vitals['BP Systolic']} mmHg",
            f"{vitals['BP Diastolic']} mmHg",
            f"{vitals['Temperature']} °C",
            f"{vitals['Glucose']} mg/dL",
            f"{vitals['SpO2']}%"
        ]
    })

    if status == "Normal":
        st.success("Your health status is NORMAL. Keep it up!")
    elif status == "Warning":
        st.warning("Some signs are outside the normal range. Please monitor closely.")
    else:
        st.error("CRITICAL condition detected. Seek medical attention immediately.")

    if send_email_alert(vitals, st.session_state.user_email, status):
        st.info("Your full health report has been emailed to you.")
    else:
        st.warning("Failed to send health report via email.")

    if st.button("Start Over"):
        st.session_state.page = 1
