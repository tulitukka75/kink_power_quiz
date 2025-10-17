# kink_power_quiz.py
# Streamlit app: Kink Power Questionnaire with fixed-per-role random order,
# per-role state persistence, radar chart, and expandable results
import json
import os
import random
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# ----------------------------
# Page setup
# ----------------------------
st.set_page_config(page_title="Kink Power Questionnaire", page_icon="🕸️", layout="centered")
st.title("Kink Power Use / Experience Questionnaire")
st.write("Rate each statement from **1 (Strongly Disagree)** to **5 (Strongly Agree)**.")

# Persistent UI flags
if "show_results" not in st.session_state:
    st.session_state["show_results"] = False

# ----------------------------
# Data loading
# ----------------------------
BASE_DIR = os.path.dirname(__file__)
QUESTIONS_PATH = os.path.join(BASE_DIR, "questions.json")
DESCRIPTIONS_PATH = os.path.join(BASE_DIR, "power_descriptions.json")

@st.cache_data(show_spinner=False)
def load_json(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# Load question bank and descriptions
try:
    QBANK = load_json(QUESTIONS_PATH)  # expects {"dom": {...}, "sub": {...}}
except Exception as e:
    st.error(f"Couldn't load questions.json: {e}")
    st.stop()

try:
    DESCRIPTIONS = load_json(DESCRIPTIONS_PATH)  # expects {Base: {"short":..., "long":...}}
except Exception as e:
    st.error(f"Couldn't load power_descriptions.json: {e}")
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

# Defensive checks
if role_key not in QBANK or not isinstance(QBANK[role_key], dict):
    st.error(f"questions.json missing role section '{role_key}'.")
    st.stop()

items = QBANK[role_key]

# ----------------------------
# Fixed random order per role (stable seeds)
# ----------------------------
@st.cache_data(show_spinner=False)
def get_fixed_order_for_role(items_dict, seed: int):
    """Return a stable shuffled list of (base, question) for this role."""
    pairs = [(base, q) for base, qlist in items_dict.items() for q in qlist]
    rnd = random.Random(seed)
    rnd.shuffle(pairs)
    return pairs

seed = 42 if role_key == "dom" else 4242
all_questions = get_fixed_order_for_role(items, seed)

# ----------------------------
# Ensure per-role answer maps exist
# ----------------------------
if "answers_dom" not in st.session_state:
    st.session_state["answers_dom"] = {}
if "answers_sub" not in st.session_state:
    st.session_state["answers_sub"] = {}

answers_map = st.session_state["answers_dom"] if role_key == "dom" else st.session_state["answers_sub"]

# ----------------------------
# Collect responses (no visible category titles)
# ----------------------------
st.markdown("### Your Responses")

current_role_scores = {base: [] for base in CATEGORIES_ORDER}

for i, (base, question) in enumerate(all_questions, start=1):
    # slider key is unique per role and index in that role's fixed order
    key = f"{role_key}-{i}"
    default_val = int(answers_map.get(key, 3))
    val = st.slider(question, min_value=1, max_value=5, value=default_val, key=key)
    answers_map[key] = val
    if base in current_role_scores:
        current_role_scores[base].append(val)

# Compute averages for visible role
scores = {
    base: (sum(vals) / len(vals)) if vals else 0
    for base, vals in current_role_scores.items()
}

# ----------------------------
# Results controls
# ----------------------------
col1, col2 = st.columns([1, 1])
with col1:
    if st.button("Show My Results", key=f"show_results_btn_{role_key}"):
        st.session_state["show_results"] = True
with col2:
    if st.button("Reset results view", key=f"reset_results_btn_{role_key}"):
        st.session_state["show_results"] = False

# ----------------------------
# Render results
# ----------------------------
if st.session_state["show_results"]:
    labels = [b for b in CATEGORIES_ORDER if b in scores]
    values = [scores[b] for b in labels]
    # close the radar
    values += values[:1]
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    # Fixed axis & orientation
    ax.set_ylim(0, 5)
    ax.set_yticks([1, 2, 3, 4, 5])
    ax.set_yticklabels(["1", "2", "3", "4", "5"])
    ax.set_theta_offset(np.pi / 2)   # start at 12 o'clock
    ax.set_theta_direction(-1)       # clockwise
    ax.grid(True)

    # Radar
    ax.plot(angles, values, linewidth=2)
    ax.fill(angles, values, alpha=0.25)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)
    ax.set_title(f"Your Power Profile – {role}", pad=20)

    st.pyplot(fig)

    # ---- Bases of power list with click-to-expand details ----
    ordered = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)

    st.markdown("### Bases of Power — details")
    for base, score in ordered:
        desc = DESCRIPTIONS.get(base, {})
        short_text = desc.get("short", "")
        long_text = desc.get("long", "")
        label = f"**{base}** — {score:.1f} · {short_text}"
        with st.expander(label, expanded=False):
            if long_text:
                st.markdown(long_text)
            else:
                st.caption("Description not available.")
