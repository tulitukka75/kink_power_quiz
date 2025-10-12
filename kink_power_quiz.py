# kink_power_quiz.py
# Streamlit app: Kink Power Questionnaire with Dom/Sub toggle + instant radar chart

import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="Kink Power Questionnaire", page_icon="🕸️", layout="centered")
st.title("Kink Power Use / Experience Questionnaire")
st.write("Rate each statement from **1 (Strongly Disagree)** to **5 (Strongly Agree)**.")

# ----------------------------
# Question banks (Dom vs Sub)
# ----------------------------
DOM_ITEMS = {
    "Legitimate": [
        "We have clearly defined roles (Dominant/submissive) that guide how we interact.",
        "Titles, rituals, or symbols (e.g., honorifics, collars) reinforce my authority.",
        "I use formal structure (protocols, rules, check-ins) to sustain the dynamic.",
        "Mutual agreement about my authority keeps the dynamic stable."
    ],
    "Reward": [
        "I use praise, affection, or pleasure to reinforce good behavior.",
        "I grant privileges (e.g., attention, permissions, orgasms) as recognition.",
        "Positive reinforcement is typically more effective than punishment in our dynamic.",
        "I deliberately create moments of joy or pride as part of power exchange."
    ],
    "Coercive": [
        "I use punishment or correction when boundaries or rules are broken.",
        "I may withhold pleasure or attention intentionally to guide behavior.",
        "Discipline scenes or consequences help maintain our structure.",
        "Correction is a form of care when applied fairly and consistently."
    ],
    "Referent": [
        "My power comes primarily from emotional connection and trust.",
        "I invest in closeness before I claim authority.",
        "I want my partner to follow because they want to, not because they must.",
        "Our bond makes submission feel natural."
    ],
    "Expert": [
        "My confidence comes from skill (e.g., rope, impact, hypnosis, safety).",
        "I study techniques and theory to improve my dominance.",
        "Competence shown through action makes me feel powerful.",
        "Authority in scenes is earned through expertise, not only title."
    ],
    "Informational": [
        "I explain the ‘why’ behind what I do when appropriate.",
        "I use words and tone to shape the emotional experience of a scene.",
        "I help my partner understand the intent behind actions or rules.",
        "Debriefing strengthens trust and our dynamic."
    ],
}

SUB_ITEMS = {
    "Legitimate": [
        "Our dynamic feels stronger when our roles are clearly defined.",
        "Titles, rituals, or symbols help me stay in the right mindset.",
        "I feel safer when my Dominant sets clear rules or protocols.",
        "When expectations are unclear, I feel ungrounded."
    ],
    "Reward": [
        "Praise or affection from my Dominant motivates me more than punishment.",
        "I look forward to rewards (attention, touch, permission) as signs of approval.",
        "I feel proud when my Dominant recognizes my effort or obedience.",
        "Rewards help me understand how to please my Dominant."
    ],
    "Coercive": [
        "I accept punishment or correction as part of my submission.",
        "Denial or discipline feels meaningful when done with care.",
        "Consequences remind me of the seriousness of our dynamic.",
        "I feel safer when consequences are consistent and fair."
    ],
    "Referent": [
        "My willingness to obey comes mostly from trust and affection.",
        "I follow more easily when I feel emotionally connected.",
        "I care deeply about my Dominant’s opinion of me.",
        "When our bond is strong, rules and control feel natural."
    ],
    "Expert": [
        "I feel safer when my Dominant shows skill and knowledge.",
        "Their competence helps me relax and surrender more deeply.",
        "I follow instructions more readily when they know their craft.",
        "Their focus on learning and safety strengthens my trust."
    ],
    "Informational": [
        "I appreciate when my Dominant explains what’s happening or why.",
        "Understanding reasons helps me stay present and calm.",
        "Their words and tone shape how I experience the scene.",
        "Debriefing or talking after scenes helps me feel understood."
    ],
}

# ----------------------------
# Role toggle & question set
# ----------------------------
role = st.radio(
    "I am answering as a…",
    options=["Dominant / Top", "Submissive / Bottom"],
    horizontal=True
)

items = DOM_ITEMS if role == "Dominant / Top" else SUB_ITEMS

# ----------------------------
# Collect responses
# ----------------------------
st.markdown("### Your Responses")
scores = {}
for base, qlist in items.items():
    st.subheader(base)
    total = 0
    for i, q in enumerate(qlist, start=1):
        # unique keys to avoid collisions if role is switched
        key = f"{role}-{base}-{i}"
        total += st.slider(q, min_value=1, max_value=5, value=3, key=key)
    scores[base] = total / len(qlist)

# ----------------------------
# Show results (radar chart)
# ----------------------------
if st.button("Show My Results"):
    labels = list(scores.keys())
    values = list(scores.values())

    # Close the radar shape
    values += values[:1]
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    # Keep 0..5 scale so sliders map 1–5 correctly
    ax.set_ylim(0, 5)
    ax.set_yticks([1, 2, 3, 4, 5])
    ax.set_yticklabels(["1", "2", "3", "4", "5"])  # or [] if you want them hidden
    ax.grid(True)

    ax.plot(angles, values, linewidth=2)
    ax.fill(angles, values, alpha=0.25)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)
    ax.set_yticklabels([])
    ax.set_title(f"Your Power Profile – {role}", pad=20)

    st.pyplot(fig)

    # Simple textual summary
    st.markdown("### Quick Read")
    sorted_bases = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
    top3 = ", ".join([f"{name} ({score:.1f})" for name, score in sorted_bases[:3]])
    st.write(f"Your strongest bases right now: **{top3}**.")
    st.caption("Tip: Compare these results with your partner’s to spot overlaps and gaps. "
               "Scores reflect preferences today; they can shift by scene and context.")
