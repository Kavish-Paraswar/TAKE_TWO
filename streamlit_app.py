import streamlit as st
import requests

API = "https://take-two.onrender.com"
# API = "http://127.0.0.1:8000"

st.title("Creative Ops Desk")

brief_title = st.text_input("Brief Title")
brief_desc = st.text_area("Brief Description")

if st.button("Start Creative Run"):
    payload = {"title": brief_title, "description": brief_desc}
    r = requests.post(API + "/runs/start", json={"brief_id": brief_id})
    if r.status_code == 200:
        st.success("Run started: " + r.json()["run_id"])
    else:
        st.error("Failed to start run")

if st.button("View Outputs"):
    r = requests.get(API + "/runs")
    st.write(r.json())
