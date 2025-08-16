import streamlit as st
import openai

# Page config
st.set_page_config(page_title="Translate My Thought", layout="centered")

st.title("🕊️ Translate My Thought")
st.markdown("Type anything you're thinking or feeling. One line. Honest. Raw. Let it go.")

# User input
user_input = st.text_area("Your thought:", placeholder="e.g. 'I feel stuck and overwhelmed.'", height=100)

# Translate button
if st.button("🔁 Translate"):
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
        st.write("🔑 API Key loaded:", openai.api_key[:5] + "...")
        
        try:
            openai.api_key = st.secrets["openai_api_key"]
            response = openai.ChatCompletion.create(
                model="gpt-4",
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
