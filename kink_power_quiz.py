import json
import os
import random
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="Kink Power Questionnaire", page_icon="🕸️", layout="centered")
st.title("Kink Power Use / Experience Questionnaire")
st.write("Rate each statement from **1 (Strongly Disagree)** to **5 (Strongly Agree)**.")

# ----------------------------
# Load question banks from JSON
# ----------------------------
QUESTIONS_PATH = os.path.join(os.path.dirname(__file__), "questions.json")

@st.cache_data(show_spinner=False)
def load_questions(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

try:
    QBANK = load_questions(QUESTIONS_PATH)
except Exception as e:
    st.error(f"Couldn't load questions.json: {e}")
    st.stop()

CATEGORIES_ORDER = ["Legitimate", "Reward", "Coercive", "Referent", "Expert", "Informational"]

# ----------------------------
# Role selection
# ----------------------------
role = st.radio(
    "I am answering as a…",
    options=["Dominant / Top", "Submissive / Bottom"],
    horizontal=True
)

role_key = "dom" if role == "Dominant / Top" else "sub"
items = QBANK[role_key]

# ----------------------------
# Build or recall a randomized question order
# ----------------------------
if "question_order" not in st.session_state or st.session_state.get("role_key") != role_key:
    # Flatten questions into (category, text) pairs
    all_questions = [(base, q) for base, qlist in items.items() for q in qlist]
    random.shuffle(all_questions)
    st.session_state["question_order"] = all_questions
    st.session_state["role_key"] = role_key
else:
    all_questions = st.session_state["question_order"]

# ----------------------------
# Collect responses (no titles)
# ----------------------------
st.markdown("### Your Responses")

responses = {base: [] for base in CATEGORIES_ORDER}

for i, (base, question) in enumerate(all_questions, start=1):
    key = f"{role_key}-{i}"
    score = st.slider(question, min_value=1, max_value=5, value=3, key=key)
    responses[base].append(score)

# ----------------------------
# Compute base averages
# ----------------------------
scores = {base: (sum(vals) / len(vals)) if vals else 0 for base, vals in responses.items()}

# ----------------------------
# Show results (radar chart)
# ----------------------------
if st.button("Show My Results"):
    labels = [b for b in CATEGORIES_ORDER if b in scores]
    values = [scores[b] for b in labels]
    values += values[:1]
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))

    # --- Fix axis scaling and orientation ---
    ax.set_ylim(0, 5)
    ax.set_yticks([1, 2, 3, 4, 5])
    ax.set_yticklabels(["1", "2", "3", "4", "5"])
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.grid(True)

