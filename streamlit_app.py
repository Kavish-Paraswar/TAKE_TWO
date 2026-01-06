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
            data = r.json()
            st.session_state.brief_id = data["id"]
            st.session_state.client_token = data.get("client_token", data.get("token"))
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
            st.session_state.run_id = data["run_id"]
            st.session_state.client_token = data.get("client_token", data.get("token"))
            st.success("Run started: " + str(st.session_state.run_id))
        else:
            st.error("Run start failed: " + r.text)

if "run_id" in st.session_state:
    st.sidebar.write("Active Run ID: " + str(st.session_state.run_id))

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Run Status")

        run_id = st.session_state.run_id
        token = st.session_state.client_token

        r = requests.get(
            API + f"/runs/{run_id}/status",
            params={"token": token}
        )

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

        run_id = st.session_state.run_id
        token = st.session_state.client_token

        if st.button("Approve Run"):
            r = requests.post(
                API + f"/runs/{run_id}/approve",
                params={"token": token}
            )

            if r.status_code == 200:
                st.success("Run approved successfully")
            else:
                st.error("Approve failed: " + r.text)

        if st.button("Interrupt Run"):
            r = requests.post(
                API + f"/runs/{run_id}/interrupt",
                params={"token": token}
            )

            if r.status_code == 200:
                st.warning("Run interrupted")
                st.session_state.pop("run_id")
            else:
                st.error("Interrupt failed: " + r.text)

    st.subheader("Agent Activity Timeline")

    run_id = st.session_state.run_id
    token = st.session_state.client_token

    r = requests.get(
        API + f"/runs/{run_id}/agents",
        params={"token": token}
    )

    if r.status_code == 200:
        logs = r.json()

        for entry in logs:
            agent = entry.get("agent", "")
            content = entry.get("content", "")
            iteration = entry.get("iteration", 0)

            st.markdown(
                "**Agent:** " + str(agent.upper())
            )
            st.write("Iteration: " + str(iteration))
            st.json(content)
    else:
        st.error("Could not load agent logs: " + r.text)

    st.subheader("Generated Outputs")

    run_id = st.session_state.run_id
    token = st.session_state.client_token

    r = requests.get(
        API + f"/runs/{run_id}/outputs",
        params={"token": token}
    )

    if r.status_code == 200:
        outputs = r.json()

        if not outputs:
            st.write("No outputs generated yet.")
        else:
            for o in outputs:
                task_name = o.get("task", "Untitled")
                score = o.get("score", "NA")

                st.subheader("Creative Output Task")
                st.write("Task: " + str(task_name))
                st.write("Score: " + str(score))

                if o.get("asset_url"):
                    st.image(o["asset_url"])
    else:
        st.error("Could not fetch outputs: " + r.text)

    st.sidebar.subheader("Manual Refresh")

    if st.sidebar.button("Refresh Dashboard"):
        r = requests.get(API + f"/runs/{st.session_state.run_id}/status", params={"token": st.session_state.client_token})
        if r.status_code == 200:
            st.success("Dashboard refreshed")
        else:
            st.error("Refresh failed: " + r.text)

    time.sleep(2)
