# ==========================================================
# 🩺 Health Care Monitor - Streamlit App
# Developed by: Ashok V
# Description: Collects user health vitals and sends email alerts if critical
# ==========================================================

import streamlit as st
import pandas as pd
import smtplib
from email.message import EmailMessage
from datetime import datetime

# -------------------------------
# Load Email Credentials Securely
# -------------------------------
EMAIL_ADDRESS = st.secrets["credentials"]["email"]
EMAIL_PASSWORD = st.secrets["credentials"]["password"]

# -------------------------------
# Evaluate Health Condition
# -------------------------------
def evaluate_status(vitals: dict) -> str:
    critical_count = 0
    if vitals['Heart Rate'] < 60 or vitals['Heart Rate'] > 120:
        critical_count += 1
    if vitals['BP Systolic'] > 140 or vitals['BP Diastolic'] > 90:
        critical_count += 1
    if vitals['Temperature'] > 38.5:
        critical_count += 1
    if vitals['Glucose'] > 180:
        critical_count += 1
    if vitals['SpO2'] < 92:
        critical_count += 1

    if critical_count == 0:
        return "Normal"
    elif critical_count <= 2:
        return "Warning"
    else:
        return "Critical"

# -------------------------------
# Send Email Alert
# -------------------------------
def send_email(vitals: dict, receiver_email: str) -> bool:
    msg = EmailMessage()
    msg['Subject'] = '🚨 Critical Health Alert'
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = receiver_email

    msg.set_content(f"""
    A critical health condition has been detected.

    Vitals Report:
    - Heart Rate: {vitals['Heart Rate']} bpm
    - Blood Pressure: {vitals['BP Systolic']}/{vitals['BP Diastolic']} mmHg
    - Temperature: {vitals['Temperature']} °C
    - Glucose: {vitals['Glucose']} mg/dL
    - SpO2: {vitals['SpO2']} %

    Please take immediate medical action.
    """)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        st.error(f"❌ Failed to send email: {e}")
        return False

# -------------------------------
# Streamlit Web App Starts Here
# -------------------------------
st.set_page_config(page_title="Health Monitor", layout="wide")
st.title("🩺 Real-Time Health Monitoring App")
st.markdown("Monitor patient vitals and send alerts if any critical thresholds are crossed.")

# Initialize session log
if "health_log" not in st.session_state:
    st.session_state.health_log = []

# -------------------------------
# Input Section
# -------------------------------
st.markdown("### 📥 Enter Your Health Report")

# Email input
user_email = st.text_input("📧 Your Email (to receive alerts)", placeholder="example@gmail.com")

# Form to input vitals
with st.form("vitals_form"):
    heart_rate = st.number_input("Heart Rate (bpm)", min_value=30, max_value=200, step=1)
    bp_sys = st.number_input("BP Systolic", min_value=80, max_value=200, step=1)
    bp_dia = st.number_input("BP Diastolic", min_value=50, max_value=130, step=1)
    temp = st.number_input("Body Temperature (°C)", min_value=34.0, max_value=42.0, step=0.1)
    glucose = st.number_input("Glucose Level (mg/dL)", min_value=50, max_value=300, step=1)
    spo2 = st.number_input("SpO2 (%)", min_value=70, max_value=100, step=1)

    submitted = st.form_submit_button("🚀 Submit Report")

# -------------------------------
# Process Data and Send Email
# -------------------------------
if submitted and user_email:
    vitals = {
        "Heart Rate": heart_rate,
        "BP Systolic": bp_sys,
        "BP Diastolic": bp_dia,
        "Temperature": temp,
        "Glucose": glucose,
        "SpO2": spo2
    }

    status = evaluate_status(vitals)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    log_entry = {
        "Email": user_email,
        "Timestamp": timestamp,
        **vitals,
        "Status": status
    }
    st.session_state.health_log.append(log_entry)

    st.success(f"✅ Your Health Status: **{status}**")

    if status == "Critical":
        if send_email(vitals, user_email):
            st.warning("📬 Alert email has been sent to the user.")
        else:
            st.error("❌ Email failed. Please check credentials or internet.")

# -------------------------------
# Display Log
# -------------------------------
if st.session_state.health_log:
    st.markdown("### 🧾 Health Report Log")
    df_log = pd.DataFrame(st.session_state.health_log)
    st.dataframe(df_log)

    st.download_button(
        label="⬇️ Download Log as CSV",
        data=df_log.to_csv(index=False).encode(),
        file_name="health_monitor_log.csv",
        mime="text/csv"
    )
