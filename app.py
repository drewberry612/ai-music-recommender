import streamlit as st
from helper import run_prompt

# ---- APP CONFIG ----
st.set_page_config(
    page_title="Wavelength",
    page_icon="🎵",
    layout="wide"
)

# ---- SESSION STATE ----
if "submitted" not in st.session_state:
    st.session_state.submitted = False
if "loading" not in st.session_state:
    st.session_state.loading = False
# if "model" not in st.session_state:
#     # Load model only once during the app session
#     st.session_state.model, st.session_state.tokenizer = load_model()
#     st.session_state.loaded = True
#     st.success("Model successfully loaded!")
# change this to ping the model to check that it is available

# ---- SIDEBAR ----
with st.sidebar:
    st.title(" 🎶 Wavelength")
    st.write(" AI-powered music recommendations")
    
    prompt = st.text_area(
        "Tell Wavelength what kind of vibe you're after:",
        placeholder="E.g. mellow acoustic songs for a rainy evening, or energetic hip-hop like Kendrick Lamar",
        height=150
    )

    if st.button("Submit"):
        if prompt.strip() != "":
            st.session_state.submitted = True
            st.session_state.loading = True
        else:
            st.warning("Please enter a valid input.")

# ---- MAIN CONTENT ----
text1 = st.empty()
text2 = st.empty()
text3 = st.empty()

if not st.session_state.submitted:
    # Introductory Section
    text1.markdown("## 🎵 Wavelength")
    text2.markdown("Welcome to **Wavelength**, your AI-powered companion for discovering music tailored to your vibe.")
    # st.image("your_logo.png", width=200)  # Replace with your logo path or URL
    text3.markdown(""" 
        #### How it works:
        - Describe the kind of music you're in the mood for — anything from vibes and feelings to specific contexts or styles.
        - Wavelength's AI will tune into your input and generate personalised track suggestions.
        - Discover music that resonates with your wavelength. 🌊
        """)
else:
    text1.empty()
    text2.empty()
    text3.empty()
    # Simulate loading time
    with st.spinner("Fetching recommendations..."):
        st.session_state.loading = False

        # Get recommendations from Spotify API
        recommendations = run_prompt(prompt)
        
        # Display recommendations
        if isinstance(recommendations, list):
            for recommendation in recommendations:
                st.markdown(f"- {recommendation}")
        else:
            st.error(recommendations)  # Display error message if the response is not a list
