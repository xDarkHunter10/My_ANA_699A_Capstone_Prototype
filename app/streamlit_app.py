import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Simple Chess Coach", page_icon="♟️", layout="centered")
st.title("♟️ Simple Chess Coach")
st.caption("A very simple demo for your capstone team: choose a mode, press a button, and get practical coaching.")

mode = st.radio(
    "What do you want to do?",
    ["Get an opening recommendation", "Analyze pasted moves", "Use a sample position", "Advanced FEN"],
)

if mode == "Get an opening recommendation":
    rating_band = st.selectbox("Your level", ["Beginner", "Intermediate"])
    color = st.selectbox("Color", ["White", "Black"])
    style = st.selectbox("Style", ["Solid", "Aggressive"])
    time_control = st.selectbox("Time control", ["Blitz", "Rapid", "Classical"])
    if st.button("Recommend an opening"):
        r = requests.post(f"{API_URL}/recommend-opening", json={
            "rating_band": rating_band,
            "color": color,
            "style": style,
            "time_control": time_control,
        }, timeout=20)
        data = r.json()
        st.subheader(data["opening"])
        st.write(data["reason"])
        st.info(data["coach_message"])

elif mode == "Analyze pasted moves":
    st.write("Paste moves like: `e4 e5 Nf3 Nc6 Bc4`")
    moves = st.text_area("Moves", "e4 e5 Nf3 Nc6 Bc4")
    if st.button("Analyze moves"):
        r = requests.post(f"{API_URL}/analyze-moves", json={"moves": moves}, timeout=20)
        data = r.json()
        st.write("Parsed moves:", " ".join(data["parsed_moves"]))
        st.success(data["summary"])
        for rec in data["recommendations"]:
            st.write(f"**{rec['move']}** — {rec['why']} ({rec['difficulty']} difficulty)")
        with st.expander("Advanced details"):
            st.code(data["fen"])

elif mode == "Use a sample position":
    positions = requests.get(f"{API_URL}/sample-positions", timeout=20).json()["positions"]
    choice = st.selectbox("Sample", list(positions.keys()))
    if st.button("Analyze sample"):
        r = requests.post(f"{API_URL}/analyze-fen", json={"fen": positions[choice]}, timeout=20)
        data = r.json()
        st.success(data["summary"])
        for rec in data["recommendations"]:
            st.write(f"**{rec['move']}** — {rec['why']} ({rec['difficulty']} difficulty)")
        with st.expander("Advanced FEN"):
            st.code(data["fen"])

else:
    fen = st.text_input("FEN", "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
    if st.button("Analyze FEN"):
        r = requests.post(f"{API_URL}/analyze-fen", json={"fen": fen}, timeout=20)
        data = r.json()
        st.success(data["summary"])
        for rec in data["recommendations"]:
            st.write(f"**{rec['move']}** — {rec['why']} ({rec['difficulty']} difficulty)")
