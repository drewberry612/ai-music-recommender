import streamlit as st
import time

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

# ---- SIDEBAR ----
with st.sidebar:
    st.title(" 🎶 Wavelength")
    st.write(" AI-powered music recommendations")
    
    # User Inputs
    prompt_type = st.selectbox("I want recommendations based on:", ["Artist", "Album", "Genre", "Song"])
    
    user_input = st.text_input(f"Enter {'a' if prompt_type in ['Genre', 'Song'] else 'an'} {prompt_type.lower()}:")

    ai_prompt = st.text_area("Provide details to tailor recommendations:", placeholder="Enter prompt here...")

    if st.button("Submit"):
        if user_input.strip() != "":
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
    - Enter an artist, album, genre, or song you like.
    - Add any extra details to help our AI fine-tune your recommendations.
    - Click "Submit" to get personalised track suggestions from our AI and Spotify integration.
    - Discover music that resonates with your wavelength. 🌊
    """)
else:
    text1.empty()
    text2.empty()
    text3.empty()
    # Simulate loading time
    with st.spinner("Fetching recommendations..."):
        time.sleep(2)  # Replace with actual API calls in your real version
        st.session_state.loading = False

        # Example Results
        st.markdown(f"""
        <div style="padding: 10px; background-color: #28a745; border-radius: 5px;">
            <p><strong>Recommendations based on:</strong></p>
            <ul>
            <li><strong>{prompt_type}:</strong> {user_input}</li>
            <li><strong>Prompt:</strong> {ai_prompt}</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("- **Track 1** - Artist A")
        st.markdown("- **Track 2** - Artist B")
        st.markdown("- **Track 3** - Artist C")
        # Replace above with actual AI/Spotify-generated content
