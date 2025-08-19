# Home.py — VIREO landing page (streamlined around your current script)
import streamlit as st
from pathlib import Path

st.set_page_config(page_title="VIREO", layout="wide")

VIREO_GREEN = "#29a329"
HERO  = Path("assets/vireo_hero.png")   # full-bleed hero (preferred)
LOGO  = Path("assets/VIREO.png")        # fallback bird/logo
THEME = Path("assets/vireo_theme.css")  # optional modern theme

# ---- Load optional theme CSS ----
if THEME.exists():
    st.markdown(f"<style>{THEME.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

# ---- Page CSS (keeps your look, tightens spacing) ----
st.markdown(f"""
<style>
.block-container {{ padding-top: 1.2rem; max-width: 900px; }}
.hero {{
  position: relative; width: 100%; border-radius: 14px; overflow: hidden;
  background: #000; box-shadow: 0 10px 30px rgba(0,0,0,.35);
}}
.hero img {{ width: 100%; height: auto; display: block; }}
.hero-caption {{
  position: absolute; left: 0; right: 0; bottom: 0;
  padding: 1.15rem 1rem; text-align: center;
  background: linear-gradient(180deg, rgba(0,0,0,0) 0%, rgba(0,0,0,.72) 100%);
  color: #fff;
}}
.brand {{ font-weight: 800; letter-spacing: .06em; font-size: 2.1rem; }}
.subtitle {{ color: {VIREO_GREEN}; font-weight: 600; }}
.lead {{ color: #c9c9c9; text-align:center; margin: 12px 0 0; }}
.cta a {{
  display:inline-block; margin-top:1rem; padding:.7rem 1.1rem; border-radius:8px;
  background:#000; color:{VIREO_GREEN}!important; border:1px solid {VIREO_GREEN};
  text-decoration:none; transition:.2s;
}}
.cta a:hover {{ background:{VIREO_GREEN}; color:#000!important; }}
.center {{ text-align:center; }}
</style>
""", unsafe_allow_html=True)

# ---- Hero (or fallback logo) ----
if HERO.exists():
    st.markdown("<div class='hero'>", unsafe_allow_html=True)
    st.image(str(HERO), use_container_width=True)
    st.markdown(
        """
        <div class='hero-caption'>
          <div class='brand'>VIREO</div>
          <div class='subtitle'>Translate my thought</div>
        </div>
        </div>
        """,
        unsafe_allow_html=True
    )
elif LOGO.exists():
    st.markdown("<div class='center'>", unsafe_allow_html=True)
    st.image(str(LOGO), width=260)
    st.markdown("</div>", unsafe_allow_html=True)
else:
    st.warning("Add a hero image at assets/vireo_hero.png (or a logo at assets/VIREO.png)")

st.markdown("<p class='lead'>A tiny tool to turn raw thoughts into one clear line.</p>", unsafe_allow_html=True)

# ---- CTA to the Translate page (Streamlit version–safe) ----
label = "🕊️ Open Translate My Thought"
if hasattr(st, "page_link"):     # Streamlit ≥ 1.32
    st.page_link("pages/01_Translate_My_Thought.py", label=label)
else:                            # Fallback for older versions
    if st.button(label):
        st.switch_page("pages/01_Translate_My_Thought.py")

st.markdown("---")
st.caption("Made with 🕊️ by VIREO")
