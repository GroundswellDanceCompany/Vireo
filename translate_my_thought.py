import streamlit as st
from openai import OpenAI
from PIL import Image
import json
import random

# -----------------------------
# Load poetic modes from JSON
# -----------------------------
with open("poetic_modes.json", "r") as f:
    poetic_modes = json.load(f)

style_names = list(poetic_modes.keys())

# -----------------------------
# Page config & Theme (VIREO green)
# -----------------------------
st.set_page_config(page_title="Translate My Thought", layout="centered")

st.markdown("""
    <style>
    html, body, [class*="css"]  { color: #29a329 !important; }
    .stButton>button {
        background-color: #29a329 !important; color: white !important;
        border: none; padding: 0.5em 1em; border-radius: 5px;
    }
    .stTextArea textarea { border: 1px solid #29a329 !important; }
    .stMarkdown, .stTextInput>div>input { color: #29a329 !important; }
    </style>
""", unsafe_allow_html=True)

# -----------------------------
# Logo
# -----------------------------
logo = Image.open("assets/VIREO.png")
st.image(logo, width=200)

# -----------------------------
# OpenAI client & sidebar settings
# -----------------------------
client = OpenAI(api_key=st.secrets["openai"]["api_key"])

st.sidebar.title("⚙️ Settings")
model_choice = st.sidebar.radio("Choose a model:", ["gpt-3.5-turbo", "gpt-4"], index=0)

# -----------------------------
# Title & intro
# -----------------------------
st.markdown("<h2 style='color:#29a329; text-align:center;'>Translate My Thought</h2>", unsafe_allow_html=True)
st.markdown("Type anything you're thinking or feeling. One line. Honest. Raw. Let it go.")

# -----------------------------
# Style selection row: Surprise Me + dropdown
# (Initialize state BEFORE rendering widgets)
# -----------------------------
if "style_select" not in st.session_state:
    st.session_state.style_select = style_names[0]

col1, col2 = st.columns([1, 3])

with col1:
    if st.button("🎲 Surprise Me"):
        st.session_state.style_select = random.choice(style_names)
        st.rerun()

with col2:
    selected_style = st.selectbox(
        "Choose a poetic style:",
        style_names,
        key="style_select"  # bound to session state
    )

# Resolved prompt & short description
resolved_prompt = poetic_modes[selected_style]
resolved_description = resolved_prompt.split(".")[0]  # first sentence as a brief description
st.markdown(
    f"<p style='color:#29a329; font-style:italic;'>“{resolved_description}.”</p>",
    unsafe_allow_html=True
)

# -----------------------------
# User input
# -----------------------------
user_input = st.text_area("Your thought:", placeholder="e.g. 'I feel stuck and overwhelmed.'", height=100)

# -----------------------------
# Translate button
# -----------------------------
if st.button("Translate"):
    if user_input.strip() == "":
        st.warning("Please enter a thought to translate.")
    else:
        messages = [
            {"role": "system", "content": resolved_prompt},
            {"role": "user", "content": user_input}
        ]
        try:
            response = client.chat.completions.create(
                model=model_choice,
                messages=messages,
                temperature=0.8,
                max_tokens=60
            )
            poetic_response = response.choices[0].message.content.strip()
            st.markdown("### 🌸 Your Line:")
            st.success(poetic_response)
        except Exception as e:
            st.error(f"Something went wrong: {e}")

# -----------------------------
# Footer
# -----------------------------
st.markdown("---")
st.markdown("<div style='color:#29a329;'>Made with 🕊️ by VIREO</div>", unsafe_allow_html=True)
