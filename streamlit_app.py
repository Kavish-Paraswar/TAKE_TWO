import streamlit as st
import requests
import time

API = "https://take-two.onrender.com"

st.set_page_config(page_title="Creative Ops Desk", layout="wide")

st.title("Creative Ops Desk - Director Dashboard")

st.sidebar.header("Director Controls")

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

if "brief_id" in st.session_state and st.button("Start Creative Run"):
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

if "run_id" in st.session_state:
    run_id = st.session_state.run_id
    token = st.session_state.client_token

    st.subheader("Live Run Activity Timeline")

    r = requests.get(API + f"/runs/{run_id}/agents", params={"token": token})

    if r.status_code == 200:
        logs = r.json()

        for entry in logs:
            agent = entry.get("agent")
            content = entry.get("content")
            iteration = entry.get("iteration", 0)

            if agent == "critic":
                score = content.get("score")
                feedback = content.get("feedback")

                st.markdown(
                    f"""
                    **Critic Review – Iteration {iteration}**

                    Score: **{score}**

                    Feedback: {feedback}
                    """
                )

            elif agent == "planner":
                tasks = content.get("tasks")

                st.markdown(
                    f"""
                    **Planner Output**

                    Planned Tasks: {tasks}
                    """
                )

            elif agent == "manager":
                st.markdown(
                    f"""
                    **Manager Update**

                    {content}
                    """
                )

            else:
                st.info(str(agent) + ": " + str(content))

    else:
        st.error("Could not load agent activity: " + r.text)

    st.subheader("Generated Assets")

    r = requests.get(API + f"/runs/{run_id}/outputs", params={"token": token})

    if r.status_code == 200:
        outputs = r.json()

        if outputs:
            grid = st.columns(2)

            for idx, o in enumerate(outputs):
                with grid[idx % 2]:
                    asset_url = o.get("asset_url")
                    score = o.get("score")

                    st.image(asset_url, caption="Score: " + str(score))
        else:
            st.write("No images generated yet. Waiting for critic scoring...")

    else:
        st.error("Could not fetch generated outputs: " + r.text)

    st.sidebar.subheader("Run Actions")

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