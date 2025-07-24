
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random
import smtplib
from email.message import EmailMessage

# Configuration
SENDER_EMAIL = "info@psacademy.sa"
SENDER_PASSWORD = st.secrets["EMAIL_PASSWORD"]  # Add this in Streamlit Cloud secrets
MARKETING_EMAIL = "info@psacademy.sa"

# Page setup
st.set_page_config(page_title="PS Academy AI Scheduler", layout="centered")
st.title("📅 PS Academy – AI Course Scheduler with Email Notifications")

st.sidebar.header("Upload Excel Data")
course_file = st.sidebar.file_uploader("Upload Public Courses File", type=["xlsx"])
trainer_file = st.sidebar.file_uploader("Upload Trainers File", type=["xlsx"])

def send_email(subject, body, to):
    msg = EmailMessage()
    msg.set_content(body)
    msg["Subject"] = subject
    msg["From"] = SENDER_EMAIL
    msg["To"] = to
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.starttls()
            smtp.login(SENDER_EMAIL, SENDER_PASSWORD)
            smtp.send_message(msg)
        return True
    except Exception as e:
        st.error(f"Failed to send email to {to}: {e}")
        return False

if course_file and trainer_file:
    course_df = pd.read_excel(course_file)
    trainer_df = pd.read_excel(trainer_file)

    course_ids = course_df["Course ID"].tolist()
    selected_course_id = st.selectbox("🗂 Select a Course to Schedule", course_ids)

    if st.button("📤 Schedule & Email Notifications"):
        course = course_df[course_df["Course ID"] == selected_course_id].iloc[0]
        duration = int(course["Duration (Days)"])
        preferred_month = course["Preferred Month"]

        eligible_trainers = trainer_df[trainer_df["Courses Can Teach"].str.contains(selected_course_id, na=False)]
        if eligible_trainers.empty:
            st.error("❌ No available trainer for this course.")
        else:
            selected_trainer = eligible_trainers.sample(1).iloc[0]

            month_map = {"January": 1, "February": 2, "March": 3, "April": 4,
                         "May": 5, "June": 6, "July": 7, "August": 8,
                         "September": 9, "October": 10, "November": 11, "December": 12}
            month_num = month_map.get(preferred_month, datetime.now().month)
            year = datetime.now().year
            start_date = datetime(year, month_num, random.randint(1, 20))
            end_date = start_date + timedelta(days=duration - 1)

            st.subheader("✅ Scheduled Course")
            st.markdown(f"**Course Title:** {course['Course Title (EN)']}")
            st.markdown(f"**Trainer:** {selected_trainer['Name']}")
            st.markdown(f"**Start Date:** {start_date.strftime('%Y-%m-%d')}")
            st.markdown(f"**End Date:** {end_date.strftime('%Y-%m-%d')}")
            st.markdown(f"**Mode:** {course['Delivery Mode']}")

            en_post = f"New Course: {course['Course Title (EN)']} by {selected_trainer['Name']} from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"

            # Send emails
            trainer_email_body = f"""
Dear {selected_trainer['Name']},

You have been assigned to deliver the course: {course['Course Title (EN)']}.

📅 Dates: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}
🏛️ Mode: {course['Delivery Mode']}

Please confirm your availability.

Regards,
PS Academy AI Agent
"""
            marketing_email_body = f"""
Dear Marketing Team,

Please publish the following announcement on our social media channels:

{en_post}

Trainer: {selected_trainer['Name']}
Start: {start_date.strftime('%Y-%m-%d')}
End: {end_date.strftime('%Y-%m-%d')}

Regards,
PS Academy AI Agent
"""

            sent_trainer = send_email(
                f"You've been assigned a new course – {course['Course Title (EN)']}",
                trainer_email_body,
                selected_trainer["Email"]
            )
            sent_marketing = send_email(
                f"New Course Announcement: {course['Course Title (EN)']}",
                marketing_email_body,
                MARKETING_EMAIL
            )

            if sent_trainer and sent_marketing:
                st.success("📬 Emails successfully sent to trainer and marketing team.")
else:
    st.info("⬅️ Please upload both course and trainer Excel files.")
