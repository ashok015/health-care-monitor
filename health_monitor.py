# ============================================
# Health Monitor App (Human-Written, Multi-Page Version)
# ============================================

import streamlit as st
import smtplib
from email.message import EmailMessage
from datetime import datetime

# --------------------------------------------
# Configuration (Replace with your actual credentials or use .streamlit/secrets.toml in deployment)
# --------------------------------------------
EMAIL_ADDRESS = "your_email@gmail.com"
EMAIL_PASSWORD = "your_app_password"

# --------------------------------------------
# Email alert function
# --------------------------------------------
def send_email_alert(vitals, receiver_email):
    try:
        msg = EmailMessage()
        msg['Subject'] = 'Critical Health Alert'
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = receiver_email

        content = f"""
        A critical health condition has been detected:

        Heart Rate: {vitals['Heart Rate']} bpm
        Blood Pressure: {vitals['BP Systolic']}/{vitals['BP Diastolic']}
        Temperature: {vitals['Temperature']}°C
        Glucose Level: {vitals['Glucose']} mg/dL
        SpO2: {vitals['SpO2']}%
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
        "Temperature": 37.0,
        "Glucose": 100,
        "SpO2": 97
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

    vitals['Heart Rate'] = st.number_input("Heart Rate (bpm)", min_value=30, max_value=200, value=vitals['Heart Rate'])
    vitals['BP Systolic'] = st.number_input("Systolic Blood Pressure", min_value=80, max_value=200, value=vitals['BP Systolic'])
    vitals['BP Diastolic'] = st.number_input("Diastolic Blood Pressure", min_value=50, max_value=130, value=vitals['BP Diastolic'])
    vitals['Temperature'] = st.number_input("Body Temperature (°C)", min_value=34.0, max_value=42.0, value=vitals['Temperature'], step=0.1)
    vitals['Glucose'] = st.number_input("Blood Glucose (mg/dL)", min_value=50, max_value=300, value=vitals['Glucose'])
    vitals['SpO2'] = st.number_input("Oxygen Saturation (SpO2 %)", min_value=80, max_value=100, value=vitals['SpO2'])

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
    st.write(vitals)
    st.success(f"Current Health Status: {status}")

    if status == "Critical":
        if send_email_alert(vitals, st.session_state.user_email):
            st.error("An alert email has been sent to your email address.")
        else:
            st.warning("Failed to deliver the email notification.")

    if st.button("Start Over"):
        st.session_state.page = 1
