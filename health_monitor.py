import streamlit as st
import pandas as pd
import random
import smtplib
from email.message import EmailMessage
from datetime import datetime

# ---------------------------
# Streamlit Page Setup
# ---------------------------
st.set_page_config(page_title="Health Monitor", layout="wide")

# ---------------------------
# Session State Initialization
# ---------------------------
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_email' not in st.session_state:
    st.session_state.user_email = ""
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""
if 'log' not in st.session_state:
    st.session_state.log = []

# ---------------------------
# Login Form
# ---------------------------
if not st.session_state.logged_in:
    st.title("Login to Health Monitoring System")

    with st.form("login_form"):
        user_email = st.text_input("Enter Your Email")
        user_name = st.text_input("Enter Your Name")
        login_submit = st.form_submit_button("Start Monitoring")

        if login_submit:
            if user_email and user_name:
                st.session_state.user_email = user_email
                st.session_state.user_name = user_name
                st.session_state.logged_in = True
                st.experimental_rerun()
            else:
                st.warning("Please fill in both fields to continue.")

# ---------------------------
# Vitals Generator Function
# ---------------------------
def generate_vitals():
    return {
        "Heart Rate": random.randint(55, 135),
        "BP Systolic": random.randint(95, 175),
        "BP Diastolic": random.randint(65, 105),
        "Temperature": round(random.uniform(36.2, 39.8), 1),
        "Glucose": random.randint(80, 230),
        "SpO2": random.randint(88, 100)
    }

# ---------------------------
# Health Status Evaluation
# ---------------------------
def evaluate_status(v):
    issues = 0
    if v['Heart Rate'] < 60 or v['Heart Rate'] > 120:
        issues += 1
    if v['BP Systolic'] > 140 or v['BP Diastolic'] > 90:
        issues += 1
    if v['Temperature'] > 38.5:
        issues += 1
    if v['Glucose'] > 180:
        issues += 1
    if v['SpO2'] < 92:
        issues += 1

    if issues == 0:
        return "Normal"
    elif issues <= 2:
        return "Warning"
    else:
        return "Critical"

# ---------------------------
# Email Alert Sender
# ---------------------------
def send_email_alert(vitals, receiver_email):
    from secrets import EMAIL_ADDRESS, EMAIL_PASSWORD

    msg = EmailMessage()
    msg['Subject'] = "Critical Health Alert"
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = receiver_email

    content = f"""
    Alert: A critical health condition has been detected.

    Patient: {st.session_state.user_name}
    Email: {receiver_email}

    Vitals:
    - Heart Rate: {vitals['Heart Rate']} bpm
    - Blood Pressure: {vitals['BP Systolic']}/{vitals['BP Diastolic']}
    - Temperature: {vitals['Temperature']} °C
    - Glucose: {vitals['Glucose']} mg/dL
    - SpO2: {vitals['SpO2']} %

    Please consult a healthcare provider.
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

# ---------------------------
# Monitoring Dashboard
# ---------------------------
if st.session_state.logged_in:
    st.title(f"Welcome, {st.session_state.user_name}")
    st.write("Monitor your vital signs and get alerts for critical conditions.")

    if st.button("Generate Vitals"):
        vitals = generate_vitals()
        status = evaluate_status(vitals)
        time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        log_entry = {
            "Timestamp": time,
            **vitals,
            "Status": status
        }
        st.session_state.log.append(log_entry)

        st.subheader(f"Current Status: {status}")
        st.dataframe(pd.DataFrame([log_entry]))

        if status == "Critical":
            email_sent = send_email_alert(vitals, st.session_state.user_email)
            if email_sent:
                st.success("Email alert sent successfully.")
            else:
                st.error("Failed to send alert email.")

    if st.session_state.log:
        st.subheader("Monitoring History")
        history_df = pd.DataFrame(st.session_state.log)
        st.dataframe(history_df)

        st.download_button(
            label="Download Log as CSV",
            data=history_df.to_csv(index=False).encode(),
            file_name="health_log.csv"
        )
