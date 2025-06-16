import streamlit as st
from frontend.helper import run_prompt
from PIL import Image, ImageDraw

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
if "recommendation_containers" not in st.session_state:
    st.session_state.recommendation_containers = []
if "show_recommendations" not in st.session_state:
    st.session_state.show_recommendations = False

# ---- SIDEBAR ----
MAX_CHARS = 300
MIN_CHARS = 10  # Set your desired minimum

with st.sidebar:
    # Load and round the logo image
    def add_rounded_corners(im, radius):
        # Convert to RGBA
        im = im.convert("RGBA")
        # Create rounded mask
        circle = Image.new('L', (radius * 2, radius * 2), 0)
        draw = ImageDraw.Draw(circle)
        draw.ellipse((0, 0, radius * 2, radius * 2), fill=255)
        alpha = Image.new('L', im.size, 255)
        w, h = im.size
        alpha.paste(circle.crop((0, 0, radius, radius)), (0, 0))
        alpha.paste(circle.crop((0, radius, radius, radius * 2)), (0, h - radius))
        alpha.paste(circle.crop((radius, 0, radius * 2, radius)), (w - radius, 0))
        alpha.paste(circle.crop((radius, radius, radius * 2, radius * 2)), (w - radius, h - radius))
        im.putalpha(alpha)
        return im

    logo = Image.open("frontend/logo.png")
    logo = add_rounded_corners(logo, radius=30)
    st.image(logo, use_container_width=True)

    prompt = st.text_area(
        "Tell Wavelength what kind of vibe you're after:",
        placeholder="E.g. mellow acoustic songs for a rainy evening, or energetic hip-hop like Kendrick Lamar",
        height=235
    )

    # Remove pre-submit validation and only validate on submit
    can_submit = True

    submit_clicked = st.button("Submit")  # Call once and save

    if submit_clicked:
        # Clear previous recommendations (moved from prompt clear logic)
        if st.session_state.recommendation_containers:
            for container in st.session_state.recommendation_containers:
                container.empty()
            st.session_state.recommendation_containers.clear()

        if len(prompt) > MAX_CHARS:
            st.warning(f"Please shorten your prompt to under {MAX_CHARS} characters before submitting.")
            st.session_state.show_recommendations = False
        elif len(prompt.strip()) < MIN_CHARS:
            st.warning(f"Prompt is too short. Please enter at least {MIN_CHARS} characters.")
            st.session_state.show_recommendations = False
        elif prompt.strip() == "":
            st.warning("Please enter a valid input.")
            st.session_state.show_recommendations = False
        else:
            st.session_state.submitted = True
            st.session_state.loading = True
            st.session_state.show_recommendations = True


# Custom CSS to set the sidebar background color
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap');
    html, body, [class^='css'], .stApp, .stMarkdown, .stTextInput, .stButton, .stAlert, .stTextArea, .st-bb, .st-c3, .st-c6, .st-cg, .st-ch, .st-ci, .st-cj, .st-ck, .st-cl, .st-cm, .st-cn, .st-co, .st-cp, .st-cq, .st-cr, .st-cs, .st-ct, .st-cu, .st-cv, .st-cw, .st-cx, .st-cy, .st-cz {
        font-family: 'Montserrat', sans-serif !important;
    }
    [data-testid="stSidebar"] {
        background-color: #0e052f !important;
    }
    [data-testid="stSidebar"] * {
        font-family: 'Montserrat', sans-serif !important;
        font-size: 1em !important;
    }
    [data-testid="stAlert"] {
        font-family: 'Montserrat', sans-serif !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ---- MAIN CONTENT ----
main_page_placeholders = [st.empty(), st.empty()]

if st.session_state.show_recommendations:
    for ph in main_page_placeholders:
        ph.empty()
    with st.spinner("Fetching recommendations..."):
        st.session_state.loading = False
        recommendations, metadata = run_prompt(prompt)
        if isinstance(recommendations, list):
            for recommendation in recommendations:
                container = st.empty()
                track = recommendation.get("track", "Unknown Track")
                artist = recommendation.get("artist", "Unknown Artist")
                meta_key = (track, artist)
                container.markdown(
                    f"""
                    <div style='padding: 1em; margin-bottom: 1em; border-radius: 8px; background: #b71c36; font-family: "Montserrat", sans-serif; font-size: 0.96em;'>
                        <span style='font-size: 1.05em; font-weight: bold; color: #fff;'>🎵 <a href='{metadata.get(meta_key, {}).get("track_url", "#")}' target='_blank' style='color: #fff; text-decoration: underline; font-family: "Montserrat", sans-serif; font-size: 1.05em;'>{track}</a></span><br>
                        <span style='color: #fff;'>by <b><a href='{metadata.get(meta_key, {}).get("artist_url", "#")}' target='_blank' style='color: #fff; text-decoration: underline; font-family: "Montserrat", sans-serif; font-size: 1.05em;'>{artist}</a></b></span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                st.session_state.recommendation_containers.append(container)
        else:
            st.error(recommendations)
    st.session_state.submitted = False
else:
    main_page_placeholders[0].markdown(
        """
        <span style='font-size: 2.1em; font-weight: bold; font-family: "Montserrat", sans-serif;'>Welcome to Wavelength</span><br>
        <span style='font-size: 1.2em; color:#ea2849; font-family: "Montserrat", sans-serif;'>Your AI-powered companion for discovering music tailored to your vibe.</span>
        """,
        unsafe_allow_html=True
    )
    main_page_placeholders[1].markdown(
        """
        <h4 style='margin-top:0; font-size:1.1em; font-family: "Montserrat", sans-serif;'>How it works:</h4>
        <ul style='margin-bottom:0; font-family: "Montserrat", sans-serif; font-size:0.96em;'>
            <li style='font-size:1em; font-family: "Montserrat", sans-serif;'>Describe the kind of music you're in the mood for — anything from vibes and feelings to specific contexts or styles.</li>
            <li style='font-size:1em; font-family: "Montserrat", sans-serif;'>Wavelength's AI will tune into your input and generate personalised track suggestions.</li>
            <li style='font-size:1em; font-family: "Montserrat", sans-serif;'>Discover music that resonates with your wavelength. 🌊</li>
        </ul>
        <div style='margin-top:1.5em; color:#ea2849; font-weight:bold; font-size:0.98em; font-family: "Montserrat", sans-serif;'>
            Note: Wavelength does not support conversational follow-up prompts. If you want to adjust your recommendations, please submit a new prompt (you can rephrase or refine it) to get a different set of suggestions.
        </div>
        """,
        unsafe_allow_html=True
    )

