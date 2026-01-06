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
        st.success("Brief created: " + str(st.session_state.brief_id))
    else:
        st.error("Brief creation failed")

if "brief_id" in st.session_state:
    if st.button("Start Creative Run"):
        b_id = st.session_state.brief_id

        r = requests.post(API + "/runs/start", json={"brief_id": b_id})

        if r.status_code == 200:
            st.session_state.run_id = r.json()["run_id"]
            st.success("Run started: " + st.session_state.run_id)
        else:
            st.error("Run start failed")

if "run_id" in st.session_state:
    if st.button("View Outputs"):
        r = requests.get(API + "/runs/" + st.session_state.run_id + "/outputs")
        if r.status_code == 200:
            st.write(r.json())
        else:
            st.error("Could not load outputs")

