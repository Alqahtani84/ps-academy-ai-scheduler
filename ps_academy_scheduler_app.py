
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random

st.set_page_config(page_title="PS Academy AI Scheduler", layout="centered")
st.title("PS Academy – AI Course Scheduler")

st.sidebar.header("Upload Excel Data")
course_file = st.sidebar.file_uploader("Upload Public Courses File", type=["xlsx"])
trainer_file = st.sidebar.file_uploader("Upload Trainers File", type=["xlsx"])

if course_file and trainer_file:
    course_df = pd.read_excel(course_file)
    trainer_df = pd.read_excel(trainer_file)

    course_ids = course_df["Course ID"].tolist()
    selected_course_id = st.selectbox("Select a Course to Schedule", course_ids)

    if st.button("Schedule & Generate Marketing Content"):
        course = course_df[course_df["Course ID"] == selected_course_id].iloc[0]
        duration = int(course["Duration (Days)"])
        preferred_month = course["Preferred Month"]

        eligible_trainers = trainer_df[trainer_df["Courses Can Teach"].str.contains(selected_course_id, na=False)]
        if eligible_trainers.empty:
            st.error("No available trainer for this course.")
        else:
            selected_trainer = eligible_trainers.sample(1).iloc[0]

            month_map = {"January": 1, "February": 2, "March": 3, "April": 4,
                         "May": 5, "June": 6, "July": 7, "August": 8,
                         "September": 9, "October": 10, "November": 11, "December": 12}
            month_num = month_map.get(preferred_month, datetime.now().month)
            year = datetime.now().year
            start_day = random.randint(1, 20)
            start_date = datetime(year, month_num, start_day)
            end_date = start_date + timedelta(days=duration - 1)

            st.subheader("Scheduled Course")
            st.markdown(f"**Course Title:** {course['Course Title (EN)']}")
            st.markdown(f"**Trainer:** {selected_trainer['Name']}")
            st.markdown(f"**Start Date:** {start_date.strftime('%Y-%m-%d')}")
            st.markdown(f"**End Date:** {end_date.strftime('%Y-%m-%d')}")
            st.markdown(f"**Mode:** {course['Delivery Mode']}")

            en_post = f"New Course: {course['Course Title (EN)']} by {selected_trainer['Name']} from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
            ar_post = f"Arabic post generation skipped (no 'Course Title (AR)' found)."

            st.subheader("Marketing Posts")
            st.code(en_post)
            st.code(ar_post)
else:
    st.info("Please upload both the course and trainer Excel files.")
