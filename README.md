![Wavelength Logo](frontend/logo.png)

# Natural Language Music Recommendations

Wavelength is an AI-powered web app that generates tailored music recommendations from natural language prompts like:

> “Energetic indie tracks with summery vibes that help me focus.”

Built with Python, Streamlit, and the Last.fm API, the app interprets your intent and returns relevant songs — not just by genre or mood, but by *vibe*.

🎥 Check out this [demo video](https://youtu.be/mVVzfWpgauQ) to see Wavelength in action.

---

## ✨ Key Features

- 🧠 **Natural Language Input** – Describe what you're in the mood for, just like you’d tell a friend.
- 🎵 **Real-Time Music Recommendations** – Get tracks that match your request using Last.fm metadata.
- 🔍 **LLM-Powered Prompt Interpretation** – A local or hosted language model interprets your prompt and turns it into a smart search query.
- 📊 **Clean, Intuitive UI** – Built with Streamlit for rapid interaction and instant feedback.
- 📈 **Modular Backend** – FastAPI handles routing, model communication, and logging.

---

## ⚙️ Tech Stack

- **Python** – Core app and logic  
- **Streamlit** – Frontend interface  
- **FastAPI** – Backend API for routing and logging  
- **Last.fm API** – Artist and track metadata  
- **Ollama** – Used during development for LLM inference (deployment options in progress)  
- **Requests** – For API interaction  

---

## 💡 Project Goals

- Create a more expressive and intuitive way to discover music using natural language.
- Explore how generative AI can enhance recommender systems.
- Build a functional, lightweight MVP showcasing LLM + API integration.

---

## 🏷️ Track Metadata & Tag Collection

Wavelength enriches every recommended track with detailed metadata to enhance the discovery experience. For each track, the app collects information such as album cover images, direct links to the track and artist, duration, and unique identifiers. Additionally, it fetches the most relevant tags for each track—such as genres, moods, and descriptive keywords—by querying Last.fm’s top tags for that track. This metadata not only powers a richer user interface but also enables more nuanced filtering and ranking of recommendations based on your prompt.

---

## 🔗 Deep Last.fm API Integration

The recommendation engine leverages multiple endpoints of the Last.fm API to deliver relevant results. It retrieves similar artists, top tracks for specific artists, and top tracks for particular tags or genres. By combining and intersecting these results, Wavelength simulates complex queries that the Last.fm API does not natively support. Robust error handling and response validation ensure that the app gracefully manages API limitations and data inconsistencies, providing a smooth and reliable user experience.

---

## 🚧 Limitations & Workarounds in the Recommendation Engine

The app uses the Last.fm API, which offers rich music metadata but lacks support for compound queries (e.g. "summery songs by Ed Sheeran"). As a result, user prompts containing combined concepts (like mood + artist) must be split into separate API calls.

To preserve user intent, the app performs intersection logic between artist-based and tag-based results to simulate combined recommendations.

The final list of candidates is re-evaluated by the LLM, which ranks results based on semantic relevance to the original user prompt.

These constraints highlight a common real-world challenge: building intelligent systems on top of rigid third-party APIs, while keeping user experience central.

Currently, Wavelength does not support follow-up prompts or conversational refinement of recommendations. Each request must be a new, unique prompt, as the app does not maintain conversational context or session history between queries. This ensures clarity in results but means users need to restate their preferences in full for each recommendation cycle.

<!--
Wavelength relies on the Last.fm API, which means recommendations are limited by the quality and completeness of Last.fm’s data. Some niche genres or lesser-known artists may have sparse metadata or fewer available recommendations.

Additionally, API rate limits and occasional inconsistencies in the Last.fm database can affect the speed and accuracy of results. Despite robust error handling, there may be rare cases where certain tracks or artists are missing expected metadata or tags.
-->

---

## Disclaimer

This app uses the Last.fm API solely to retrieve music recommendations and metadata. No Last.fm content is used to train, fine-tune, or otherwise develop any machine learning or AI model.  
All AI components operate on the user’s input and Last.fm’s publicly accessible API responses, and the app does not store or redistribute Last.fm data.  
This project complies with the Last.fm API Terms of Service.
