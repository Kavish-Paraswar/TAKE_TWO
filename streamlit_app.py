import streamlit as st
import requests

API = "https://take-two.onrender.com"

st.set_page_config(page_title="Creative Ops Desk", layout="wide")

st.title("Creative Ops Desk - Director Dashboard")

st.sidebar.header("Run Controls")

title = st.text_input("Brief Title")
description = st.text_area("Brief Description")

# create brief
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

# start run
if "brief_id" in st.session_state:
    st.sidebar.write("Active Brief ID: " + str(st.session_state.brief_id))

    if st.button("Start Creative Run"):
        r = requests.post(
            API + "/runs/start",
            params={"title": title, "description": description}
        )

        if r.status_code == 200:
            data = r.json()
            st.session_state.run_id = data["run_id"]
            st.session_state.client_token = data.get("client_token", data.get("token"))
            st.success("Run started: " + str(st.session_state.run_id))
        else:
            st.error("Run start failed: " + r.text)

# show run details
if "run_id" in st.session_state:
    run_id = st.session_state.run_id
    token = st.session_state.client_token

    st.sidebar.subheader("Director Decisions")

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
            st.success("Run approved successfully")
        else:
            st.error("Approve failed: " + r.text)

    st.subheader("Agent Activity Timeline")

    r = requests.get(API + f"/runs/{run_id}/agents", params={"token": token})

    if r.status_code == 200:
        logs = r.json()

        for entry in logs:
            agent = entry.get("agent", "")
            content = entry.get("content", "")
            iteration = entry.get("iteration", 0)

            if agent == "planner":
                st.info("Planner - Planned tasks for iteration " + str(iteration))

            elif agent == "critic":
                st.markdown(
                    "**Critic Review - Iteration " + str(iteration) + "**"
                )
                st.json(content)

            elif agent == "manager":
                st.info("Manager - " + str(content))

            else:
                st.write(str(agent) + " - " + str(content))

    else:
        st.error("Could not load agent logs: " + r.text)

    st.subheader("Creative Outputs")

    r = requests.get(API + f"/runs/{run_id}/outputs", params={"token": token})

    if r.status_code == 200:
        outputs = r.json()

        if not outputs:
            st.write("No outputs generated yet")
        else:
            for o in outputs:
                st.markdown(
                    "**Task:** " + o.get("task", "Untitled")
                )
                st.progress(o.get("score", 0))
                st.write("Score: " + str(o.get("score", "NA")))
    else:
        st.error("Could not fetch outputs: " + r.text)
