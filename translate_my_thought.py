import streamlit as st
from PIL import Image
from openai import OpenAI
import json, random, urllib.parse
from streamlit.components.v1 import html

# -------------------------
# Config
# -------------------------
LOGO_PATH = "assets/VIREO.png"
VIREO_GREEN = "#29a329"
PAGE_TITLE = "VIREO — Translate My Thought"

# -------------------------
# Data
# -------------------------
with open("poetic_modes.json", "r") as f:
    poetic_modes = json.load(f)
style_names = list(poetic_modes.keys())

# -------------------------
# Page / Theme
# -------------------------
st.set_page_config(page_title=PAGE_TITLE, layout="centered")
st.markdown(f"""
    <style>
    html, body, [class*="css"]  {{ color: {VIREO_GREEN} !important; }}
    .stButton>button {{
        background: black !important; color: {VIREO_GREEN} !important;
        border: 1px solid {VIREO_GREEN}; padding: 0.5em 1em; border-radius: 6px; cursor: pointer;
    }}
    .stTextArea textarea {{ border: 1px solid {VIREO_GREEN} !important; }}
    .share-btn {{
        display:inline-block; margin:4px; padding:6px 12px; font-size:14px;
        background:black; color:{VIREO_GREEN} !important; border:1px solid {VIREO_GREEN};
        border-radius:6px; text-decoration:none; transition:.2s;
    }}
    .share-btn:hover {{ background:{VIREO_GREEN}; color:black !important; }}
    .status-pill {{
        float:right; font-size:12px; padding:4px 8px; border-radius:999px;
        border:1px solid {VIREO_GREEN}; color:{VIREO_GREEN};
    }}
    </style>
""", unsafe_allow_html=True)

# -------------------------
# Logo + Title
# -------------------------
st.image(Image.open(LOGO_PATH), width=200)
st.markdown(f"<h2 style='color:{VIREO_GREEN}; text-align:center;'>Translate My Thought</h2>", unsafe_allow_html=True)

# -------------------------
# Mode: Auto-detect Demo/API
# -------------------------
api_key = None
try:
    api_key = st.secrets["openai"]["api_key"]
except Exception:
    api_key = None

demo_mode = api_key is None
if demo_mode:
    st.markdown(f"<div class='status-pill'>Demo mode</div>", unsafe_allow_html=True)
else:
    st.markdown(f"<div class='status-pill'>API mode</div>", unsafe_allow_html=True)

client = OpenAI(api_key=api_key) if not demo_mode else None

# -------------------------
# Style picker (Surprise + Dropdown)
# -------------------------
if "style_select" not in st.session_state:
    st.session_state.style_select = style_names[0]

col1, col2 = st.columns([1, 3])
with col1:
    if st.button("🎲 Surprise Me"):
        st.session_state.style_select = random.choice(style_names)
        st.rerun()
with col2:
    selected_style = st.selectbox("Style", style_names, key="style_select")

resolved_prompt = poetic_modes[selected_style]
resolved_description = resolved_prompt.split(".")[0]
st.markdown(f"<p style='color:{VIREO_GREEN}; font-style:italic;'>“{resolved_description}.”</p>", unsafe_allow_html=True)

# -------------------------
# Input
# -------------------------
user_input = st.text_area("Your thought:", placeholder="e.g. 'I feel stuck and overwhelmed.'", height=100)

# -------------------------
# Demo translator (no API)
# -------------------------
def demo_translate(thought: str, style: str) -> str:
    t = (thought or "this moment").strip()
    samples = {
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
    return samples.get(style, f"{t} turns toward light.")

# -------------------------
# Copy-to-clipboard (no deps)
# -------------------------
def copy_button(text: str, label: str = "📋 Copy line"):
    safe = text.replace("\\", "\\\\").replace("`", "\\`").replace('"', '\\"').replace("\n", "\\n")
    html(f"""
        <button onclick="navigator.clipboard.writeText(`{safe}`)"
                style="background:black;color:{VIREO_GREEN};border:1px solid {VIREO_GREEN};
                       padding:8px 12px;border-radius:6px;cursor:pointer;">
            {label}
        </button>
    """, height=45)

# -------------------------
# Translate
# -------------------------
poetic_response = None
if st.button("Translate"):
    if not user_input.strip():
        st.warning("Please enter a thought to translate.")
    else:
        if demo_mode:
            poetic_response = demo_translate(user_input, selected_style)
            st.markdown("### 🌿 Your Line (Demo):")
            st.success(poetic_response)
        else:
            try:
                messages = [
                    {"role": "system", "content": resolved_prompt},
                    {"role": "user", "content": user_input}
                ]
                resp = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    temperature=0.8,
                    max_tokens=60
                )
                poetic_response = resp.choices[0].message.content.strip()
                st.markdown("### 🌸 Your Line:")
                st.success(poetic_response)
            except Exception as e:
                st.error(f"API error: {e}")
                st.info("Falling back to Demo.")
                poetic_response = demo_translate(user_input, selected_style)
                st.success(poetic_response)

# -------------------------
# Share (auto-append #VIREO)
# -------------------------
if poetic_response:
    st.markdown("#### Share")
    share_text = f"{poetic_response}  #VIREO"
    copy_button(share_text)

    encoded = urllib.parse.quote(share_text)
    twitter   = f"https://twitter.com/intent/tweet?text={encoded}"
    whatsapp  = f"https://wa.me/?text={encoded}"
    telegram  = f"https://t.me/share/url?url=&text={encoded}"
    mailto    = f"mailto:?subject=VIREO%20line&body={encoded}"
    fb        = f"https://www.facebook.com/sharer/sharer.php?u=https://github.com/yourname/vireo&quote={encoded}"
    threads   = f"https://www.threads.net/intent/post?text={encoded}"
    instagram = "https://www.instagram.com/"  # paste copied line manually

    st.markdown(
        f"""
        <a class="share-btn" href="{twitter}" target="_blank">X/Twitter</a>
        <a class="share-btn" href="{whatsapp}" target="_blank">WhatsApp</a>
        <a class="share-btn" href="{telegram}" target="_blank">Telegram</a>
        <a class="share-btn" href="{mailto}" target="_blank">Email</a>
        <a class="share-btn" href="{fb}" target="_blank">Facebook</a>
        <a class="share-btn" href="{threads}" target="_blank">Threads</a>
        <a class="share-btn" href="{instagram}" target="_blank" title="Copy first, then paste into Instagram">Instagram</a>
        """,
        unsafe_allow_html=True
    )

# -------------------------
# Footer
# -------------------------
st.markdown("---")
st.markdown(f"<div style='color:{VIREO_GREEN};'>Made with 🕊️ by VIREO</div>", unsafe_allow_html=True)
