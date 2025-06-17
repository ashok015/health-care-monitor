import streamlit as st
import pandas as pd
import smtplib
from email.message import EmailMessage
from datetime import datetime

# Page config
st.set_page_config(page_title="Health Monitor", layout="wide")

# Session state setup
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_email' not in st.session_state:
    st.session_state.user_email = ""
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""
if 'log' not in st.session_state:
    st.session_state.log = []

# Login form
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
                st.warning("Please fill in both fields.")

# Health condition checker
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

# Email alert sender
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
        st.error(f"Could not send alert email: {e}")
        return False

# Main app after login
if st.session_state.logged_in:
    st.title(f"Welcome, {st.session_state.user_name}")
    st.write("Please fill in your latest medical report.")

    with st.form("vitals_form"):
        heart_rate = st.number_input("Heart Rate (bpm)", min_value=30, max_value=200)
        bp_sys = st.number_input("BP Systolic", min_value=70, max_value=200)
        bp_dia = st.number_input("BP Diastolic", min_value=40, max_value=120)
        temp = st.number_input("Body Temperature (°C)", min_value=34.0, max_value=43.0, format="%.1f")
        glucose = st.number_input("Glucose (mg/dL)", min_value=40, max_value=300)
        spo2 = st.number_input("SpO2 (%)", min_value=60, max_value=100)

        submit_vitals = st.form_submit_button("Submit")

        if submit_vitals:
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

            entry = {
                "Timestamp": timestamp,
                **vitals,
                "Status": status
            }

            st.session_state.log.append(entry)

            st.subheader(f"Current Status: {status}")
            st.dataframe(pd.DataFrame([entry]))

            if status == "Critical":
                if send_email_alert(vitals, st.session_state.user_email):
                    st.success("Critical alert sent to your email.")
                else:
                    st.error("Failed to send email.")

    if st.session_state.log:
        st.subheader("Your Monitoring History")
        df = pd.DataFrame(st.session_state.log)
        st.dataframe(df)
        st.download_button("Download CSV Report", data=df.to_csv(index=False).encode(), file_name="health_report.csv")
