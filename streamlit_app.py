import streamlit as st
import requests

API = "https://take-two.onrender.com"

st.title("Creative Ops Desk")

title = st.text_input("Brief Title")
description = st.text_area("Brief Description")

if st.button("Create Brief"):
    payload = {"title": title, "description": description}
    r = requests.post(API + "/briefs/", json=payload)

    if r.status_code == 200:
        st.session_state.brief_id = r.json()["id"]
        st.success("Brief created:", st.session_state.brief_id)
    else:
        st.error("Brief creation failed:", r.text)

if st.button("Start Creative Run"):
    r = requests.post(
        API + "/runs/start",
        params={
            "title": title,
            "description": description
        }
    )

    if r.status_code == 200:
        st.session_state.run_id = r.json()["run_id"]
        st.success("Run started: " + str(st.session_state.run_id))

    else:
        st.error("Run start failed:", r.text)

