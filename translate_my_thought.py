import streamlit as st
from openai import OpenAI
from PIL import Image

# Load and display logo
logo = Image.open("assets/VIREO.png")  # Adjust path if needed
st.image(logo, width=150)  # Adjust width as desired
    

# Page config
st.set_page_config(page_title="Translate My Thought", layout="centered")

# Inject custom green theme styling
st.markdown("""
    <style>
    html, body, [class*="css"]  {
        color: #29a329 !important;  /* Vireo green */
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

# Load API key
client = OpenAI(api_key=st.secrets["openai"]["api_key"])

# Sidebar: Model selector
st.sidebar.title("⚙️ Settings")
model_choice = st.sidebar.radio(
    "Choose a model:",
    options=["gpt-3.5-turbo", "gpt-4"],
    index=0  # Default to GPT-3.5
)

# App Title
st.title("Translate My Thought")
st.markdown("Type anything you're thinking or feeling. One line. Honest. Raw. Let it go.")

# User input
user_input = st.text_area(
    "Your thought:",
    placeholder="e.g. 'I feel stuck and overwhelmed.'",
    height=100
)

# Translate button
if st.button("Translate"):
    if user_input.strip() == "":
        st.warning("Please enter a thought to translate.")
    else:
        system_prompt = """
        You are a poetic translator. Take any input — raw, honest, angry, sad, mundane — and return a one-line poetic response.
        Your response should be emotionally intelligent, metaphorical, gentle, and resonant.
        Speak like a friend who understands the soul. Keep it short. Never explain.
        """

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]

        try:
            response = openai.ChatCompletion.create(
                model=model_choice,
                messages=messages,
                temperature=0.8,
                max_tokens=60
            )
            poetic_response = response.choices[0].message["content"].strip()
            st.markdown("### 🌸 Your Line:")
            st.success(poetic_response)

        except Exception as e:
            st.error(f"Something went wrong: {e}")

# Footer
st.markdown("---")
st.markdown("Made with 🕊️ by VIREO")
