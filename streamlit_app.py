import streamlit as st
import requests
import time

API = "https://take-two.onrender.com"

st.set_page_config(page_title="Creative Ops Desk", layout="wide")

st.title("Creative Ops Desk - Director Panel")

st.sidebar.header("Controls")

title = st.text_input("Brief Title")
description = st.text_area("Brief Description")

if st.button("Create Brief"):
    if not title or not description:
        st.error("Title and description are required")
    else:
        payload = {"title": title, "description": description}
        r = requests.post(API + "/briefs/", json=payload)

        if r.status_code == 200:
            st.session_state.brief_id = r.json()["id"]
            st.success("Brief created: " + str(st.session_state.brief_id))
        else:
            st.error("Brief creation failed: " + r.text)

if "brief_id" in st.session_state:
    st.sidebar.write("Active Brief ID: " + str(st.session_state.brief_id))

    if st.button("Start Creative Run"):
        params = {
            "title": title,
            "description": description
        }

        r = requests.post(API + "/runs/start", params=params)

        if r.status_code == 200:
            data = r.json()

            # save only the keys that really exist
            st.session_state.run_id = data["run_id"]

            # fixed token handling safely
            if "client_token" in data:
                st.session_state.client_token = data["client_token"]
            elif "token" in data:
                st.session_state.client_token = data["token"]
            else:
                st.session_state.client_token = None

            st.success("Run started: " + str(st.session_state.run_id))
        else:
            st.error("Run start failed: " + r.text)

if "run_id" in st.session_state:
    run_id = st.session_state.run_id
    token = st.session_state.get("client_token")

    st.sidebar.write("Active Run ID: " + str(run_id))

    st.subheader("Run Status")

    r = requests.get(API + f"/runs/{run_id}/status", params={"token": token})

    if r.status_code == 200:
        data = r.json()

        st.json(data)
        progress = data.get("progress", 0)
        st.progress(progress / 100)
    else:
        st.error("Could not fetch status: " + r.text)

    st.subheader("Agent Timeline Logs")

    r = requests.get(API + f"/runs/{run_id}/agents", params={"token": token})

    if r.status_code == 200:
        logs = r.json()
        for msg in logs:
            st.info(f"{msg.get('agent','AGENT')} : {msg.get('content','')}")
    else:
        st.error("Could not load agent logs: " + r.text)

    st.subheader("Generated Outputs")

    r = requests.get(API + f"/runs/{run_id}/outputs", params={"token": token})

    if r.status_code == 200:
        outputs = r.json()
        for o in outputs:
            if o.get("asset_url"):
                st.image(o["asset_url"], caption="Score: " + str(o.get("score","NA")))
    else:
        st.error("Could not fetch outputs: " + r.text)

    if st.sidebar.button("Interrupt Run"):
        r = requests.post(API + f"/runs/{run_id}/interrupt", params={"token": token})
        if r.status_code == 200:
            st.warning("Run interrupted")
            st.session_state.pop("run_id")
        else:
            st.error("Interrupt failed: " + r.text)

    if st.sidebar.button("Approve Run"):
        r = requests.post(API + f"/runs/{run_id}/approve", params={"token": token})
        if r.status_code == 200:
            st.success("Run approved")
        else:
            st.error("Approval failed: " + r.text)

    time.sleep(5)
    st.experimental_rerun()
