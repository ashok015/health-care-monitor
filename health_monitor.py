# ============================================
# Health Monitor App (Professional Developer Version)
# ============================================

import streamlit as st
import smtplib
from email.message import EmailMessage
from datetime import datetime

# --------------------------------------------
# Configuration (Use .streamlit/secrets.toml for production)
# --------------------------------------------
EMAIL_ADDRESS = "your_email@gmail.com"
EMAIL_PASSWORD = "your_app_password"

# --------------------------------------------
# Email alert function
# --------------------------------------------
def send_email_alert(vitals, receiver_email):
    try:
        msg = EmailMessage()
        msg['Subject'] = 'Health Alert Notification'
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = receiver_email

        content = f"""
        A health concern has been identified:

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
# Evaluate the vitals
# --------------------------------------------
def evaluate_health(vitals):
    issues = 0
    if vitals['Heart Rate'] < 60 or vitals['Heart Rate'] > 100:
        issues += 1
    if vitals['BP Systolic'] > 140 or vitals['BP Diastolic'] > 90:
        issues += 1
    if vitals['Temperature'] > 37.5:
        issues += 1
    if vitals['Glucose'] > 140:
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
# Streamlit app config
# --------------------------------------------
st.set_page_config(page_title="Health Monitor App", layout="centered")

# --------------------------------------------
# Initialize session states
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
        "SpO2": 98
    }

# --------------------------------------------
# PAGE 1 – User Login
# --------------------------------------------
if st.session_state.page == 1:
    st.title("Health Monitor: Login")
    st.write("Enter your name and email to proceed.")

    st.session_state.user_name = st.text_input("Your Name")
    st.session_state.user_email = st.text_input("Email for Alerts")

    if st.button("Next"):
        if st.session_state.user_name and st.session_state.user_email:
            st.session_state.page = 2
        else:
            st.warning("Please enter both name and email.")

# --------------------------------------------
# PAGE 2 – Data Collection
# --------------------------------------------
elif st.session_state.page == 2:
    st.title("Medical Report Input")
    st.write("Fill in your current vital stats.")

    vitals = st.session_state.vitals

    vitals['Heart Rate'] = st.number_input("Heart Rate (bpm)", 40, 180, vitals['Heart Rate'])
    vitals['BP Systolic'] = st.number_input("Systolic Pressure", 80, 200, vitals['BP Systolic'])
    vitals['BP Diastolic'] = st.number_input("Diastolic Pressure", 50, 130, vitals['BP Diastolic'])
    vitals['Temperature'] = st.number_input("Body Temperature (°C)", 35.0, 42.0, vitals['Temperature'], 0.1)
    vitals['Glucose'] = st.number_input("Blood Glucose (mg/dL)", 70, 300, vitals['Glucose'])
    vitals['SpO2'] = st.number_input("SpO2 (%)", 85, 100, vitals['SpO2'])

    if st.button("Generate Report"):
        st.session_state.page = 3

# --------------------------------------------
# PAGE 3 – Patient Report
# --------------------------------------------
elif st.session_state.page == 3:
    st.title("Health Report")

    vitals = st.session_state.vitals
    status = evaluate_health(vitals)

    st.subheader(f"Patient Name: {st.session_state.user_name}")
    st.markdown("### Report Summary")

    col1, col2, col3 = st.columns(3)
    col1.metric("Heart Rate", f"{vitals['Heart Rate']} bpm")
    col2.metric("BP", f"{vitals['BP Systolic']}/{vitals['BP Diastolic']}")
    col3.metric("Temperature", f"{vitals['Temperature']}°C")

    col4, col5, col6 = st.columns(3)
    col4.metric("Glucose", f"{vitals['Glucose']} mg/dL")
    col5.metric("SpO2", f"{vitals['SpO2']}%")
    col6.metric("Status", status)

    if status == "Critical":
        if send_email_alert(vitals, st.session_state.user_email):
            st.error("Alert email sent successfully.")
        else:
            st.warning("Failed to send alert email.")
    elif status == "Warning":
        st.warning("Please monitor your health closely.")
    else:
        st.success("All vitals are within normal range.")

    if st.button("Restart"):
        st.session_state.page = 1
