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
            st.session_state.run_id = r.json()["run_id"]
            st.success("Run started: " + str(st.session_state.run_id))
        else:
            st.error("Run start failed: " + r.text)

if "run_id" in st.session_state:
    st.sidebar.write("Active Run ID: " + str(st.session_state.run_id))

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Run Status")

        status_url = API + f"/runs/{st.session_state.run_id}/status"
        r = requests.get(status_url)

        if r.status_code == 200:
            data = r.json()
            st.json(data)

            progress = data.get("progress", 0)
            st.progress(progress / 100)

            st.write("Current State: " + data.get("state", "UNKNOWN"))
            st.write("Iteration: " + str(data.get("iteration", 0)))
            st.write("Budget Used: " + str(data.get("budget_used", 0)))
        else:
            st.error("Could not fetch status: " + r.text)

    with col2:
        st.subheader("Director Actions")

        if st.button("Approve Run"):
            r = requests.post(API + f"/runs/{st.session_state.run_id}/approve")

            if r.status_code == 200:
                st.success("Run approved successfully")
            else:
                st.error("Approve failed: " + r.text)

        if st.button("Interrupt Run"):
            r = requests.post(API + f"/runs/{st.session_state.run_id}/interrupt")

            if r.status_code == 200:
                st.warning("Run interrupted")
                st.session_state.pop("run_id")
            else:
                st.error("Interrupt failed: " + r.text)

    st.subheader("Agent Timeline Logs")

    agents_url = API + f"/runs/{st.session_state.run_id}/agents"
    r = requests.get(agents_url)

    if r.status_code == 200:
        logs = r.json()

        for msg in logs:
            agent = msg.get("agent", "AGENT")
            content = msg.get("content", "")
            iteration = msg.get("iteration", 0)

            st.info(f"[Iteration {iteration}] {agent}: {content}")
    else:
        st.error("Could not load agent logs: " + r.text)

    st.subheader("Generated Outputs")

    outputs_url = API + f"/runs/{st.session_state.run_id}/outputs"
    r = requests.get(outputs_url)

    if r.status_code == 200:
        outputs = r.json()

        if not outputs:
            st.write("No outputs generated yet. Refreshing automatically...")
        else:
            cols = st.columns(3)

            for idx, o in enumerate(outputs):
                with cols[idx % 3]:
                    asset = o.get("asset_url")
                    score = o.get("score", "NA")

                    if asset:
                        st.image(asset, caption="Score: " + str(score))
                    else:
                        st.write("Asset unavailable")
    else:
        st.error("Could not fetch outputs: " + r.text)

    st.sidebar.subheader("Auto Refresh")

    if st.sidebar.button("Refresh Now"):
        st.experimental_rerun()

    time.sleep(2)

