import streamlit as st
from PIL import Image
from openai import OpenAI
import json, random, urllib.parse
from streamlit.components.v1 import html

# -------------------------
# Config
# -------------------------
VIREO_GREEN = "#29a329"
PAGE_TITLE = "VIREO — Translate My Thought"

# -------------------------
# Data
# -------------------------
with open("poetic_modes.json", "r", encoding="utf-8") as f:
    poetic_modes = json.load(f)

# Build style list (exclude _meta)
style_names = [k for k in poetic_modes.keys() if k != "_meta"]

# Helper to pull prompt/desc and examples for a style
def get_style_block(modes, name):
    block = modes[name]
    if isinstance(block, dict):
        prompt = block.get("prompt", "")
        examples = block.get("examples", [])
    else:
        prompt = str(block)
        examples = []
    # First sentence (up to first period) as a short description
    desc = prompt.split(".")[0].strip() if prompt else ""
    return prompt, desc, examples

# Build messages with system prefix + style prompt + few-shots + user
def build_messages(modes, style_name, user_text):
    sys_prefix = modes["_meta"]["system_prefix"]
    style_prompt, _, examples = get_style_block(modes, style_name)

    msgs = [
        {"role": "system", "content": sys_prefix},
        {"role": "system", "content": style_prompt},
    ]
    for ex in examples:
        t = ex.get("thought", "").strip()
        l = ex.get("line", "").strip()
        if t and l:
            msgs.append({"role": "user", "content": t})
            msgs.append({"role": "assistant", "content": l})
    msgs.append({"role": "user", "content": user_text.strip()})
    return msgs

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
    .error-pill {{
        display:inline-block; font-size:12px; padding:4px 8px; border-radius:999px;
        border:1px solid #ff4d4f; color:#ff4d4f; margin-left:6px;
    }}
    </style>
""", unsafe_allow_html=True)

from pathlib import Path
theme_css = Path("assets/vireo_theme.css").read_text(encoding="utf-8")
st.markdown(f"<style>{theme_css}</style>", unsafe_allow_html=True)

st.markdown(
    """
    <div style="text-align:center; margin: .6rem 0 1.1rem;">
      <h1 id="vireo-title" style="margin:0; font-weight:800; font-size:2.6rem;">VIREO</h1>
      <h3 style="margin:.3rem 0 0; font-weight:500; font-size:1rem; color:#29a329;">
        Translate my thought
      </h3>
    </div>
    """, unsafe_allow_html=True
)

# -------------------------
# Logo / Title
# -------------------------
st.markdown(
    """
    <div style="text-align:center; margin-bottom: 2rem;">
        <h1 style="color:white; font-size: 3rem; font-weight: 800; margin:0;">VIREO</h1>
        <h3 style="color:#29a329; font-size: 1.2rem; font-weight: 500; margin-top:0.5rem;">
            Translate my thought
        </h3>
    </div>
    """,
    unsafe_allow_html=True
)

# -------------------------
# Sidebar: Mode + Paywall
# -------------------------
st.sidebar.title("⚙️ Mode")
mode = st.sidebar.radio("Select mode:", ["Demo (free)", "API (paid)"], index=0)

checkout_url = None
try:
    checkout_url = st.secrets["paywall"].get("checkout_url", None)
except Exception:
    checkout_url = None

if mode == "API (paid)":
    valid_codes = []
    try:
        cfg = st.secrets["paywall"]
        if isinstance(cfg.get("codes"), list):
            valid_codes = [str(c).strip() for c in cfg["codes"]]
        elif isinstance(cfg.get("code"), str):
            valid_codes = [cfg["code"].strip()]
    except Exception:
        pass

    access_code = st.sidebar.text_input("Access code", type="password")
    if checkout_url:
        st.sidebar.markdown(f"[Buy access →]({checkout_url})")

    api_key = None
    try:
        api_key = st.secrets["openai"]["api_key"]
    except Exception:
        api_key = None

    code_ok = (access_code.strip() in valid_codes) if valid_codes else False
    api_ok  = api_key is not None and len(api_key.strip()) > 0

    if not code_ok or not api_ok:
        st.markdown(f"<div class='status-pill'>API mode (locked)</div>", unsafe_allow_html=True)
        if not code_ok:
            st.sidebar.markdown("<span class='error-pill'>Invalid or missing access code</span>", unsafe_allow_html=True)
        if not api_ok:
            st.sidebar.markdown("<span class='error-pill'>Missing OpenAI API key</span>", unsafe_allow_html=True)
        client = None
        demo_mode = True
    else:
        st.markdown(f"<div class='status-pill'>API mode</div>", unsafe_allow_html=True)
        client = OpenAI(api_key=api_key)
        demo_mode = False
else:
    st.markdown(f"<div class='status-pill'>Demo mode</div>", unsafe_allow_html=True)
    client = None
    demo_mode = True

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
    selected_style = st.selectbox("Poetic Style", style_names, key="style_select")

style_prompt, style_desc, _ = get_style_block(poetic_modes, selected_style)
if style_desc:
    st.markdown(f"<p style='color:{VIREO_GREEN}; font-style:italic;'>“{style_desc}.”</p>", unsafe_allow_html=True)

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
        "Shakespearean": f"{t} weighs the hour; still, I answer dawn.",
        "Deep": f"The root of {t} is asking to be seen.",
        "Comic": f"{t}? You’re not broken—you’re buffering. Try a heart refresh.",
        "Zen": f"{t} is a cloud; the sky remains.",
        "Mystical": f"Within {t}, a hidden lantern waits for your name.",
        "Mythic Mirror": f"You stand at the gate of {t}; the key is your true name.",
        "Haiku": f"{t} in one breath— old knots loosening— spring finds a door",
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
                messages = build_messages(poetic_modes, selected_style, user_input)
                resp = client.chat.completions.create(
                    model="gpt-3.5-turbo",  # or "gpt-4o-mini" for slightly better tone at low cost
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
    instagram = "https://www.instagram.com/"

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
