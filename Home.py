import streamlit as st
from pathlib import Path

st.set_page_config(page_title="VIREO", layout="wide")

HERO = Path("assets/vireo_hero.png")  # change to .png if needed
VIREO_GREEN = "#29a329"

# --- Simple CSS to reduce padding + center content
st.markdown(f"""
<style>
.block-container {{ padding-top: 1.5rem; max-width: 900px; }}
.hero {{
  position: relative; width: 100%; border-radius: 14px; overflow: hidden;
  background: #000; box-shadow: 0 10px 30px rgba(0,0,0,.35);
}}
.hero img {{ width: 100%; height: auto; display: block; }}
.hero-caption {{
  position: absolute; left: 0; right: 0; bottom: 0;
  padding: 1.25rem 1rem; text-align: center;
  background: linear-gradient(180deg, rgba(0,0,0,0) 0%, rgba(0,0,0,.7) 100%);
  color: #fff;
}}
.brand {{ font-weight: 800; letter-spacing: .06em; }}
.subtitle {{ color: {VIREO_GREEN}; font-weight: 500; }}
.cta a {{
  display:inline-block; margin-top:1rem; padding:.7rem 1.1rem; border-radius:8px;
  background:#000; color:{VIREO_GREEN}!important; border:1px solid {VIREO_GREEN};
  text-decoration:none; transition:.2s;
}}
.cta a:hover {{ background:{VIREO_GREEN}; color:#000!important; }}
</style>
""", unsafe_allow_html=True)

# --- Hero
if HERO.exists():
    st.markdown("<div class='hero'>", unsafe_allow_html=True)
    st.image(str(HERO), use_column_width=True)
    st.markdown(
        f"""
        <div class='hero-caption'>
          <div class='brand' style='font-size:2.2rem;'>VIREO</div>
          <div class='subtitle'>Translate my thought</div>
        </div>
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    st.warning("Add your image at assets/vireo_hero.jpg")

st.write("")
st.write("A tiny tool to turn raw thoughts into one clear line.")

# --- CTA to app page (Streamlit multipage)
# Put your main app in pages/01_Translate_My_Thought.py
st.markdown(
    "<div class='cta'><a href='pages/01_Translate_My_Thought.py'>🕊️ Open Translate My Thought</a></div>",
    unsafe_allow_html=True
)

st.markdown("---")
st.caption("Made with 🕊️ by VIREO")
