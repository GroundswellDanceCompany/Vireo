import streamlit as st
from openai import OpenAI
from PIL import Image
import json, random

# --- Load poetic modes from JSON (must be next to this script) ---
with open("poetic_modes.json", "r") as f:
    poetic_modes = json.load(f)

style_names = list(poetic_modes.keys())

# --- THEME (VIREO green) ---
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

# --- LOGO ---
logo = Image.open("assets/VIREO.png")
st.image(logo, width=200)

# --- API client ---
client = OpenAI(api_key=st.secrets["openai"]["api_key"])

# --- Sidebar: Model toggle (keeps costs flexible) ---
st.sidebar.title("⚙️ Settings")
model_choice = st.sidebar.radio("Choose a model:", ["gpt-3.5-turbo", "gpt-4"], index=0)

# --- Title & intro ---
st.markdown("<h2 style='color:#29a329; text-align:center;'>Translate My Thought</h2>", unsafe_allow_html=True)
st.markdown("Type anything you're thinking or feeling. One line. Honest. Raw. Let it go.")

# --- Style selection row: dropdown + Surprise Me button ---
# Keep a stable index in session_state so the button can update the dropdown
if "style_index" not in st.session_state:
    st.session_state.style_index = 0  # default to first style

col1, col2 = st.columns([3, 1])
with col1:
    selected_style = st.selectbox(
        "🎭 Choose a poetic style:",
        style_names,
        index=st.session_state.style_index,
        key="style_select"
    )
with col2:
    if st.button("🎲 Surprise Me"):
        st.session_state.style_index = random.randrange(len(style_names))
        # Update the selectbox value too
        st.session_state.style_select = style_names[st.session_state.style_index]
        st.experimental_rerun()

# Ensure selected_style reflects the current index/value
selected_style = st.session_state.get("style_select", style_names[st.session_state.style_index])

# --- Brief description under selected style (first sentence of prompt) ---
resolved_prompt = poetic_modes[selected_style]
resolved_description = resolved_prompt.split(".")[0]  # show first sentence only
st.markdown(f"<p style='color:#29a329; font-style:italic;'>“{resolved_description}.”</p>", unsafe_allow_html=True)

# --- Input ---
user_input = st.text_area("Your thought:", placeholder="e.g. 'I feel stuck and overwhelmed.'", height=100)

# --- Translate ---
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

# --- Footer ---
st.markdown("---")
st.markdown("<div style='color:#29a329;'>Made with 🕊️ by VIREO</div>", unsafe_allow_html=True)
