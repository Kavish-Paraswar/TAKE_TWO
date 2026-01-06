import streamlit as st
import requests
import time

API = "https://take-two.onrender.com"

st.set_page_config(page_title="Creative Ops Desk", layout="wide")

st.title("Creative Ops Desk - Director Panel")

st.sidebar.header("Controls")

title = st.text_input("Brief Title")
description = st.text_area("Brief Description")

# create brief only once
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

# show active brief info
if "brief_id" in st.session_state:
    st.sidebar.write("Active Brief ID: " + str(st.session_state.brief_id))

    # start creative run only once per brief
    if st.button("Start Creative Run"):
        r = requests.post(API + "/runs/start", params={
            "title": title,
            "description": description
        })

        if r.status_code == 200:
            data = r.json()
            st.session_state.run_id = data["run_id"]
            st.session_state.client_token = data["client_token"]
            st.success("Run started: " + str(st.session_state.run_id))
        else:
            st.error("Run start failed: " + r.text)

# once run started, show dashboard
if "run_id" in st.session_state:
    st.sidebar.write("Active Run ID: " + str(st.session_state.run_id))

    status_url = API + f"/runs/{st.session_state.run_id}/status"
    agents_url = API + f"/runs/{st.session_state.run_id}/agents"
    outputs_url = API + f"/runs/{st.session_state.run_id}/outputs"
    approve_url = API + f"/runs/{st.session_state.run_id}/approve"
    interrupt_url = API + f"/runs/{st.session_state.run_id}/interrupt"

    token = st.session_state.client_token

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Run Status")

        # auto refresh status
        r = requests.get(status_url, params={"token": token})

        if r.status_code == 200:
            data = r.json()

            st.json(data)

            progress = data.get("progress", 0)
            st.progress(progress / 100)

            st.write("Current State: " + str(data.get("state", "UNKNOWN")))
            st.write("Iteration: " + str(data.get("iteration", 0)))
            st.write("Budget Used: " + str(data.get("budget_used", 0)))
        else:
            st.error("Could not fetch status: " + r.text)

    with col2:
        st.subheader("Director Actions")

        # approve run
        if st.button("Approve Run"):
            r = requests.post(approve_url, params={"token": token})

            if r.status_code == 200:
                st.success("Run approved successfully")
            else:
                st.error("Approve failed: " + r.text)

        # interrupt run
        if st.button("Interrupt Run"):
            r = requests.post(interrupt_url, params={"token": token})

            if r.status_code == 200:
                st.warning("Run interrupted")
                st.session_state.pop("run_id")
                st.session_state.pop("client_token")
            else:
                st.error("Interrupt failed: " + r.text)

    # show agent timeline logs
    st.subheader("Agent Timeline Logs")

    r = requests.get(agents_url, params={"token": token})

    if r.status_code == 200:
        logs = r.json()

        if not logs:
            st.write("No agent messages yet. Refreshing...")
        else:
            for msg in logs:
                agent = msg.get("agent", "AGENT")
                content = msg.get("content", "")
                iteration = msg.get("iteration", 0)

                st.info(f"[Iteration {iteration}] {agent}: {content}")
    else:
        st.error("Could not load agent logs: " + r.text)

    # show generated outputs
    st.subheader("Generated Outputs Gallery")

    r = requests.get(outputs_url, params={"token": token})

    if r.status_code == 200:
        outputs = r.json()

        if not outputs:
            st.write("No outputs generated yet. Refreshing automatically...")
            time.sleep(2)
            st.experimental_rerun()
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

    st.sidebar.subheader("Manual Refresh")

    if st.sidebar.button("Refresh Dashboard"):
        st.experimental_rerun()

    # refresh every 5 seconds
    st.sidebar.write("Auto-refreshing status every 5 seconds...")
    time.sleep(5)
    st.experimental_rerun()
