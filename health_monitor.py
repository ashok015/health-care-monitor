# ============================================
# Health Monitor App (Final Clean Version)
# ============================================

import streamlit as st
import smtplib
from email.message import EmailMessage
from datetime import datetime
import os

# --------------------------------------------
# Load email credentials from secrets.toml
# --------------------------------------------
EMAIL_ADDRESS = st.secrets["credentials"]["email"]
EMAIL_PASSWORD = st.secrets["credentials"]["password"]

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
        st.warning("Email error: " + str(e))
        return False

# --------------------------------------------
# Health evaluation function
# --------------------------------------------
def evaluate_health(vitals):
    issues = 0
    if vitals['Heart Rate'] < 60 or vitals['Heart Rate'] > 100:
        issues += 1
    if vitals['BP Systolic'] > 140 or vitals['BP Diastolic'] > 90:
        issues += 1
    if vitals['Temperature'] > 38.0:
        issues += 1
    if vitals['Glucose'] > 180:
        issues += 1
    if vitals['SpO2'] < 95:
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
def page_1():
    st.title("Welcome to Health Monitor")
    st.write("Please enter your details to proceed.")

    name = st.text_input("Full Name")
    email = st.text_input("Your Email Address")

    if st.button("Next"):
        if name and email:
            st.session_state.user_name = name
            st.session_state.user_email = email
            st.session_state.page = 2
        else:
            st.warning("Please fill in all fields.")

# --------------------------------------------
# PAGE 2 – MEDICAL ENTRY
# --------------------------------------------
def page_2():
    st.title("Enter Medical Report")
    vitals = st.session_state.vitals

    vitals['Heart Rate'] = st.number_input("Heart Rate (bpm)", min_value=30, max_value=200, value=vitals['Heart Rate'])
    vitals['BP Systolic'] = st.number_input("Systolic BP", min_value=80, max_value=200, value=vitals['BP Systolic'])
    vitals['BP Diastolic'] = st.number_input("Diastolic BP", min_value=50, max_value=130, value=vitals['BP Diastolic'])
    vitals['Temperature'] = st.number_input("Temperature (°C)", min_value=34.0, max_value=42.0, value=vitals['Temperature'])
    vitals['Glucose'] = st.number_input("Glucose Level (mg/dL)", min_value=50, max_value=300, value=vitals['Glucose'])
    vitals['SpO2'] = st.number_input("SpO2 (%)", min_value=80, max_value=100, value=vitals['SpO2'])

    if st.button("Generate Report"):
        st.session_state.page = 3

# --------------------------------------------
# PAGE 3 – SUMMARY
# --------------------------------------------
def page_3():
    st.title("Health Report")
    vitals = st.session_state.vitals
    status = evaluate_health(vitals)

    st.subheader(f"Patient: {st.session_state.user_name}")
    st.write("### Vital Signs Summary")
    st.table(vitals)
    st.info(f"Health Status: {status}")

    if status == "Critical":
        success = send_email_alert(vitals, st.session_state.user_email)
        if success:
            st.success("Alert email sent to user.")
        else:
            st.error("Failed to send alert email.")

    if st.button("Start Over"):
        st.session_state.page = 1

# --------------------------------------------
# Render Pages
# --------------------------------------------
if st.session_state.page == 1:
    page_1()
elif st.session_state.page == 2:
    page_2()
elif st.session_state.page == 3:
    page_3()
