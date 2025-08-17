import streamlit as st
from PIL import Image
from openai import OpenAI
import json, random

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
# Sidebar settings
# -----------------------------
st.sidebar.title("⚙️ Settings")
demo_mode = st.sidebar.checkbox("🧪 Demo mode (no API)", value=True)
model_choice = st.sidebar.radio("Model (when demo is off):", ["gpt-3.5-turbo", "gpt-4"], index=0)

# Try to create client only if not in demo mode
client = None
if not demo_mode:
    try:
        client = OpenAI(api_key=st.secrets["openai"]["api_key"])
    except Exception:
        st.sidebar.error("No valid OpenAI API key found in secrets. Using Demo mode instead.")
        demo_mode = True

# -----------------------------
# Title & intro
# -----------------------------
st.markdown("<h2 style='color:#29a329; text-align:center;'>Translate My Thought</h2>", unsafe_allow_html=True)
st.markdown("Type anything you're thinking or feeling. One line. Honest. Raw. Let it go.")

# -----------------------------
# Surprise Me + dropdown
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
        "🎭 Choose a poetic style:",
        style_names,
        key="style_select"
    )

resolved_prompt = poetic_modes[selected_style]
resolved_description = resolved_prompt.split(".")[0]
st.markdown(
    f"<p style='color:#29a329; font-style:italic;'>“{resolved_description}.”</p>",
    unsafe_allow_html=True
)

# -----------------------------
# Input
# -----------------------------
user_input = st.text_area("Your thought:", placeholder="e.g. 'I feel stuck and overwhelmed.'", height=100)

# -----------------------------
# Demo generator
# -----------------------------
def demo_translate(thought: str, style: str) -> str:
    t = thought.strip() or "this moment"
    base = {
        "Poetic": f"Like tide over stone, {t} learns to soften.",
        "Stoic": f"{t.capitalize()} is opinion; choose the next right action.",
        "Shakespearean": f"'{t}' doth weigh my breast—yet still I breathe and onward go.",
        "Deep": f"The root of {t} is asking to be seen.",
        "Comic": f"{t}? You’re not broken—you’re buffering. Try a heart refresh.",
        "Zen": f"{t} is a cloud; the sky remains.",
        "Mystical": f"Within {t}, a hidden lantern waits for your name.",
        "Mythic Mirror": f"You stand at the gate of {t}; the key is your true name.",
        "Haiku": f"{t} in one breath—\nold knots loosening slowly—\nspring finds a small door",
        "Lyrical": f"I hum through {t} till the melody turns me light.",
        "Oracular": f"From {t}, a sign: choose the narrow way and become wide.",
        "Surrealist": f"{t} grew feathers; the clock drank the sea.",
        "Romantic": f"In {t}, the heart still hears a distant, faithful lighthouse.",
        "Minimalist": f"{t}. Then—space.",
        "Elegiac": f"I lay down the old name of {t} and listen for the quiet.",
        "Epic/Grand": f"Across the ridge of {t}, your small step moves the mountain.",
        "Satirical": f"{t}? Install fewer chaos-plugins.",
        "Ecstatic (Rumi-style)": f"Beloved, even {t} is a doorway wearing your face.",
        "Journal-style": f"Today felt like {t}. One truthful line eased it.",
        "Rap/Spoken Word": f"{t} in my chest—ride the beat, let the walls confess.",
        "Childlike": f"{t} feels big. I am bigger.",
        "Cinematic": f"The room tightens with {t}; a window brightens—you exhale."
    }
    return base.get(style, f"{t} turns toward light.")

# -----------------------------
# Translate
# -----------------------------
if st.button("Translate"):
    if user_input.strip() == "":
        st.warning("Please enter a thought to translate.")
    else:
        if demo_mode or client is None:
            poetic_response = demo_translate(user_input, selected_style)
            st.markdown("### 🌸 Your Line (Demo):")
            st.success(poetic_response)
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
                st.error(f"API error: {e}")
                st.info("Falling back to Demo mode.")
                st.success(demo_translate(user_input, selected_style))

# -----------------------------
# Footer
# -----------------------------
st.markdown("---")
st.markdown("<div style='color:#29a329;'>Made with 🕊️ by VIREO</div>", unsafe_allow_html=True)
