import streamlit as st
from PIL import Image, ImageDraw, ImageFont
from openai import OpenAI
import json, random, urllib.parse, io
from streamlit.components.v1 import html

# ---------------------------------
# Config
# ---------------------------------
LOGO_PATH = "assets/VIREO.png"
FONT_PATH = None  # e.g. "assets/Inter-Regular.ttf" (optional custom font)
VIREO_GREEN = "#29a329"

# ---------------------------------
# Load poetic modes from JSON
# ---------------------------------
with open("poetic_modes.json", "r") as f:
    poetic_modes = json.load(f)
style_names = list(poetic_modes.keys())

# ---------------------------------
# Page config & Theme (VIREO green)
# ---------------------------------
st.set_page_config(page_title="Translate My Thought", layout="centered")
st.markdown(f"""
    <style>
    html, body, [class*="css"]  {{ color: {VIREO_GREEN} !important; }}
    .stButton>button {{
        background-color: {VIREO_GREEN} !important; color: white !important;
        border: none; padding: 0.5em 1em; border-radius: 5px; cursor:pointer;
    }}
    .stTextArea textarea {{ border: 1px solid {VIREO_GREEN} !important; }}
    .share-btn {{
        display:inline-block; margin-right:8px; margin-top:6px;
        background:{VIREO_GREEN}; color:white; text-decoration:none; padding:8px 10px;
        border-radius:5px; font-size:0.9rem;
    }}
    </style>
""", unsafe_allow_html=True)

# ---------------------------------
# Logo
# ---------------------------------
logo = Image.open(LOGO_PATH)
st.image(logo, width=200)

# ---------------------------------
# Sidebar settings
# ---------------------------------
st.sidebar.title("⚙️ Settings")
demo_mode = st.sidebar.checkbox("🧪 Demo mode (no API)", value=True)
model_choice = st.sidebar.radio("Model (when demo is off):", ["gpt-3.5-turbo", "gpt-4"], index=0)

# Create OpenAI client when not in demo mode
client = None
if not demo_mode:
    try:
        client = OpenAI(api_key=st.secrets["openai"]["api_key"])
    except Exception:
        st.sidebar.error("No valid OpenAI API key found in secrets. Using Demo mode instead.")
        demo_mode = True

# ---------------------------------
# Title & intro
# ---------------------------------
st.markdown(f"<h2 style='color:{VIREO_GREEN}; text-align:center;'>Translate My Thought</h2>", unsafe_allow_html=True)
st.markdown("Type anything you're thinking or feeling. One line. Honest. Raw. Let it go.")

# ---------------------------------
# Style selection row: Surprise Me + dropdown
# ---------------------------------
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
st.markdown(f"<p style='color:{VIREO_GREEN}; font-style:italic;'>“{resolved_description}.”</p>", unsafe_allow_html=True)

# ---------------------------------
# Input
# ---------------------------------
user_input = st.text_area("Your thought:", placeholder="e.g. 'I feel stuck and overwhelmed.'", height=100)

# ---------------------------------
# Demo generator (no-API)
# ---------------------------------
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

# ---------------------------------
# Copy-to-clipboard (no deps)
# ---------------------------------
def copy_button(text: str, label: str = "📋 Copy"):
    safe = text.replace("\\", "\\\\").replace("`", "\\`").replace('"', '\\"').replace("\n", "\\n")
    html(f"""
        <button onclick="navigator.clipboard.writeText(`{safe}`)"
                style="background:{VIREO_GREEN};color:white;border:none;padding:8px 12px;border-radius:5px;cursor:pointer;">
            {label}
        </button>
    """, height=45)

# ---------------------------------
# Image card generator (returns PIL Image)
# ---------------------------------
def create_share_card(quote: str, style_name: str, logo_img: Image.Image) -> Image.Image:
    W, H = 1200, 630
    bg = Image.new("RGB", (W, H), color=(0, 0, 0))
    draw = ImageDraw.Draw(bg)

    # Fonts
    try:
        title_font = ImageFont.truetype(FONT_PATH, 44) if FONT_PATH else ImageFont.load_default()
        quote_font = ImageFont.truetype(FONT_PATH, 48) if FONT_PATH else ImageFont.load_default()
        foot_font  = ImageFont.truetype(FONT_PATH, 28) if FONT_PATH else ImageFont.load_default()
    except Exception:
        title_font = ImageFont.load_default()
        quote_font = ImageFont.load_default()
        foot_font  = ImageFont.load_default()

    GREEN = (41, 163, 41)
    WHITE = (255, 255, 255)

    # Logo (top-left)
    try:
        lg = logo_img.convert("RGBA")
        lg_w = 180
        ratio = lg_w / lg.width
        lg = lg.resize((lg_w, int(lg.height * ratio)))
        bg.paste(lg, (60, 40), lg)  # keep transparency if present
    except Exception:
        pass

    # Helper: text width (compatible across Pillow versions)
    def text_width(txt, font):
        try:
            return draw.textlength(txt, font=font)
        except Exception:
            bbox = draw.textbbox((0, 0), txt, font=font)
            return bbox[2] - bbox[0]

    # Wrap text
    def wrap_text(text, font, max_w):
        words = text.split(" ")
        lines, line = [], ""
        for w in words:
            test = (line + " " + w).strip()
            if text_width(test, font) <= max_w:
                line = test
            else:
                if line:
                    lines.append(line)
                line = w
        if line:
            lines.append(line)
        return lines

    # Title (style)
    draw.text((60, 250), style_name, font=title_font, fill=GREEN)

    # Quote
    max_w = W - 120
    lines = []
    for para in quote.split("\n"):
        lines.extend(wrap_text(para, quote_font, max_w))

    y = 310
    for li in lines:
        draw.text((60, y), li, font=quote_font, fill=WHITE)
        y += 60

    # Footer
    footer = "Made with 🕊️ VIREO"
    fw = text_width(footer, foot_font)
    draw.text((W - fw - 60, H - 60), footer, font=foot_font, fill=GREEN)

    return bg  # PIL Image

# ---------------------------------
# Translate
# ---------------------------------
poetic_response = None

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
                poetic_response = demo_translate(user_input, selected_style)
                st.success(poetic_response)

# ---------------------------------
# Share & Copy (render only if we have a line)
# ---------------------------------
# -----------------------------
# Share & Copy (render only if we have a line)
# -----------------------------
if poetic_response:
    st.markdown("#### Share")
    
    # Auto-append subtle tag
    share_text = f"{poetic_response}  #VIREO"
    copy_button(share_text, "📋 Copy line")

    encoded = urllib.parse.quote(share_text)

    # ✅ X/Twitter (prefilled text)
    twitter  = f"https://twitter.com/intent/tweet?text={encoded}"

    # ✅ WhatsApp (prefilled text)
    whatsapp = f"https://wa.me/?text={encoded}"

    # ✅ Telegram (prefilled text)
    telegram = f"https://t.me/share/url?url=&text={encoded}"

    # ✅ Email
    mailto   = f"mailto:?subject=VIREO%20line&body={encoded}"

    # ✅ Facebook — requires a URL; quote can carry your line
    # Replace this with your site/repo URL when you’re ready
    share_url = "https://github.com/yourname/vireo"  
    fb = (
        "https://www.facebook.com/sharer/sharer.php?"
        f"u={urllib.parse.quote(share_url)}&quote={encoded}"
    )

    # ✅ Threads — supports text intent
    threads = f"https://www.threads.net/intent/post?text={encoded}"

    # ⚠️ Instagram — no official text intent
    instagram = "https://www.instagram.com/"

    st.markdown(
        f"""
        <a class="share-btn" href="{twitter}" target="_blank">🐦 X/Twitter</a>
        <a class="share-btn" href="{whatsapp}" target="_blank">💬 WhatsApp</a>
        <a class="share-btn" href="{telegram}" target="_blank">📨 Telegram</a>
        <a class="share-btn" href="{mailto}" target="_blank">✉️ Email</a>
        <a class="share-btn" href="{fb}" target="_blank">📘 Facebook</a>
        <a class="share-btn" href="{threads}" target="_blank">🧵 Threads</a>
        <a class="share-btn" href="{instagram}" target="_blank" title="Copy the line first, then paste into Instagram">📸 Instagram</a>
        """,
        unsafe_allow_html=True
    )

# ---------------------------------
# Footer
# ---------------------------------
st.markdown("---")
st.markdown(f"<div style='color:{VIREO_GREEN};'>Made with 🕊️ by VIREO</div>", unsafe_allow_html=True)
