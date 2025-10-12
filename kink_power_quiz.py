# kink_power_quiz.py
# Streamlit app: Kink Power Questionnaire loading questions from questions.json

import json
import os
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
        data = json.load(f)
    # Basic sanity checks
    for role in ("dom", "sub"):
        if role not in data:
            raise ValueError(f"Missing '{role}' section in questions.json")
        if not isinstance(data[role], dict) or not data[role]:
            raise ValueError(f"'{role}' must be a non-empty object of categories")
    return data

try:
    QBANK = load_questions(QUESTIONS_PATH)
except Exception as e:
    st.error(f"Couldn't load questions.json: {e}")
    st.stop()

# Ensure consistent category order
CATEGORIES_ORDER = ["Legitimate", "Reward", "Coercive", "Referent", "Expert", "Informational"]

# ----------------------------
# Role toggle & question set
# ----------------------------
role = st.radio(
    "I am answering as a…",
    options=["Dominant / Top", "Submissive / Bottom"],
    horizontal=True
)

role_key = "dom" if role == "Dominant / Top" else "sub"
items = QBANK[role_key]

# Warn if categories are missing
missing = [c for c in CATEGORIES_ORDER if c not in items]
if missing:
    st.warning(f"Missing categories in questions.json for role '{role_key}': {', '.join(missing)}")

# ----------------------------
# Collect responses
# ----------------------------
st.markdown("### Your Responses")
scores = {}
for base in CATEGORIES_ORDER:
    qlist = items.get(base, [])
    if not qlist:
        continue
    st.subheader(base)
    total = 0
    for i, q in enumerate(qlist, start=1):
        key = f"{role_key}-{base}-{i}"
        total += st.slider(q, min_value=1, max_value=5, value=3, key=key)
    scores[base] = total / len(qlist)

# ----------------------------
# Show results (radar chart)
# ----------------------------
if st.button("Show My Results"):
    # Filter to categories that actually have scores
    labels = [b for b in CATEGORIES_ORDER if b in scores]
    values = [scores[b] for b in labels]

    # Close the radar shape
    values += values[:1]
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))

    # --- Fix axis scaling and orientation ---
    ax.set_ylim(0, 5)
    ax.set_yticks([1, 2, 3, 4, 5])
    ax.set_yticklabels(["1", "2", "3", "4", "5"])
    ax.set_theta_offset(np.pi / 2)   # Start at top
    ax.set_theta_direction(-1)       # Clockwise
    ax.grid(True)

    # --- Draw the radar ---
    ax.plot(angles, values, linewidth=2)
    ax.fill(angles, values, alpha=0.25)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)
    ax.set_title(f"Your Power Profile – {role}", pad=20)

    st.pyplot(fig)

    # Simple textual summary
    st.markdown("### Quick Read")
    sorted_bases = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
    top3 = ", ".join([f"{name} ({score:.1f})" for name, score in sorted_bases[:3]])
    st.write(f"Your strongest bases right now: **{top3}**.")
    st.caption("Tip: Compare these results with your partner’s to spot overlaps and gaps. "
               "Scores reflect preferences today; they can shift by scene and context.")

