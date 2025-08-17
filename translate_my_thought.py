
import streamlit as st
from openai import OpenAI
from PIL import Image
import json

# Load poetic modes from file
with open("poetic_modes.json", "r") as f:
    poetic_modes = json.load(f)

# Inject custom green theme styling
st.markdown("""
    <style>
    html, body, [class*="css"]  {
        color: #29a329 !important;
    }
    .stButton>button {
        background-color: #29a329 !important;
        color: white !important;
        border: none;
        padding: 0.5em 1em;
        border-radius: 5px;
    }
    .stTextArea textarea {
        border: 1px solid #29a329 !important;
    }
    .stMarkdown, .stTextInput>div>input {
        color: #29a329 !important;
    }
    </style>
""", unsafe_allow_html=True)

# Load and display logo
logo = Image.open("assets/VIREO.png")
st.image(logo, width=200)

# Load API key
client = OpenAI(api_key=st.secrets["openai"]["api_key"])

# Sidebar: Model selector and poetic mode
st.sidebar.title("⚙️ Settings")
model_choice = st.sidebar.radio(
    "Choose a model:",
    options=["gpt-3.5-turbo", "gpt-4"],
    index=0
)

poetic_style = st.sidebar.selectbox("🎭 Poetic Style", list(poetic_modes.keys()), index=0)
system_prompt = poetic_modes[poetic_style]

# App Title & Description
st.markdown("<h2 style='color:#29a329; text-align:center;'>Translate My Thought</h2>", unsafe_allow_html=True)
st.markdown("Type anything you're thinking or feeling. One line. Honest. Raw. Let it go.")

# User input
user_input = st.text_area("Your thought:", placeholder="e.g. 'I feel stuck and overwhelmed.'", height=100)

# Translate button
if st.button("Translate"):
    if user_input.strip() == "":
        st.warning("Please enter a thought to translate.")
    else:
        messages = [
            {"role": "system", "content": system_prompt},
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

# Footer
st.markdown("---")
st.markdown("<div style='color:#29a329;'>Made with 🕊️ by VIREO</div>", unsafe_allow_html=True)
