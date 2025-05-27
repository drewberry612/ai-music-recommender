import streamlit as st
import requests

DOMAIN = "http://<your_local_ip>:<your_port>"
API_URL = "http://ws.audioscrobbler.com/2.0/"
API_KEY = "your_api_key_here"
PROMPT_ERROR = "Sorry, I couldn't understand your request. Please try phrasing it differently!"
API_ERROR = "Sorry, something went wrong while finding recommendations. Please try again later."
REFINE_ERROR = "Sorry, something went wrong while finalising your recommendations. Please try again."

def validate_response(response, expected_type):
    try:
        if response.status_code == 200:
            model_response = response.json()

            if expected_type == "dict":
                if isinstance(model_response, dict) and 'artist' in model_response and 'genre' in model_response and 'tags' in model_response:
                    return model_response
                else:
                    st.error("Error: Response structure is incorrect for prompt interpretation.")
                    st.stop()

            elif expected_type == "list":
                if isinstance(model_response, list):
                    return model_response
                else:
                    st.error("Error: Response structure is incorrect for recommendations refinement.")
                    st.stop()

            else:
                st.error(f"Error: Unknown expected response type '{expected_type}'.")
                st.stop()

        else:
            st.error(f"Error: Unable to process the request. Status code: {response.status_code}")
            st.stop()

    except ValueError:
        st.error("Error: Response is not valid JSON.")
        st.stop()

def safe_split(value):
    # Function to safely split the strings and handle cases where the value is empty or null
    if value and isinstance(value, str):  # Check if the value is not null and is a string
        return [item.strip() for item in value.split(',')]  # Split and strip spaces
    return []  # Return an empty list if the value is null or not a string

def interpret_prompt(prompt):
    query = (
        f"Given the prompt '{prompt}', extract the key information and return it in this exact structured format: "
        "{"
        "'artist': artist name(s), "
        "'genre': genre name(s), "
        "'tags': [tag1, tag2, ...]"
        "}. "
        "If any information is missing, use None for a missing value or an empty list for tags. "
        "Return only the structure, no additional commentary or explanation."
    )

    # Send the request to the model
    payload = {"query": query}
    response = requests.post(DOMAIN, json=payload)

    valid_response = validate_response(response, expected_type="dict")

    # Apply the safe_split function to the artist and genre fields
    valid_response['artist'] = safe_split(valid_response.get('artist', ''))
    valid_response['genre'] = safe_split(valid_response.get('genre', ''))

    return valid_response

def validate_lastfm_response(response, expected_keys):
    try:
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and any(key in data for key in expected_keys):
                return data
            else:
                st.error("Error: Response structure is incorrect or missing expected keys.")
                st.stop()
        else:
            st.error(f"Error: Last.fm API request failed with status code {response.status_code}")
            st.stop()
    except ValueError:
        st.error("Error: Last.fm response is not valid JSON.")
        st.stop()

def get_similar_artists(artist_name, limit=5):
    params = {
        'method': 'artist.getsimilar',
        'artist': artist_name,
        'api_key': API_KEY,
        'format': 'json',
        'limit': limit
    }
    response = requests.get(API_URL, params=params)
    data = validate_lastfm_response(response, expected_keys=['similarartists'])

    similar_artists = []
    if 'similarartists' in data:
        for artist in data['similarartists']['artist']:
            similar_artists.append(artist['name'])
    return similar_artists

def get_tracks_for_artist(artist_name, limit=3):
    params = {
        'method': 'artist.gettoptracks',
        'artist': artist_name,
        'api_key': API_KEY,
        'format': 'json',
        'limit': limit
    }
    response = requests.get(API_URL, params=params)
    data = validate_lastfm_response(response, expected_keys=['toptracks'])

    tracks = []
    if 'toptracks' in data:
        for track in data['toptracks']['track']:
            tracks.append(track['name'])
    return tracks

def get_recommended_tracks_by_artist(artist_name):
    similar_artists = get_similar_artists(artist_name)
    all_tracks = []

    for artist in similar_artists:
        tracks = get_tracks_for_artist(artist)
        for track in tracks:
            all_tracks.append((artist, track))  # (artist name, track name)
    
    return all_tracks

def get_recommended_tracks_by_tag(tag):
    params = {
        'method': 'tag.gettoptracks',
        'tag': tag,
        'api_key': API_KEY,
        'format': 'json',
        'limit': 5
    }
    response = requests.get(API_URL, params=params)
    data = validate_lastfm_response(response, expected_keys=['tracks'])

    tracks = []
    if 'tracks' in data:
        for track in data['tracks']['track']:
            tracks.append((track['artist']['name'], track['name']))  # (tag name, track name)
    
    return tracks

def get_recommended_tracks_by_track(track_name):
    params = {
        'method': 'track.getsimilar',
        'track': track_name,
        'api_key': API_KEY,
        'format': 'json',
        'limit': 5
    }
    response = requests.get(API_URL, params=params)
    data = validate_lastfm_response(response, expected_keys=['similartracks'])

    tracks = []
    if 'similartracks' in data:
        for track in data['similartracks']['track']:
            tracks.append((track['artist']['name'], track['name']))  # (artist name, track name)
    
    return tracks

def get_recommendations(parsed_prompt):
    recommendations = []

    for artist in parsed_prompt['artist']:
        if artist:
            recommendations.extend(get_recommended_tracks_by_artist(artist))

    for tag in parsed_prompt['tag']:
        if tag:
            recommendations.extend(get_recommended_tracks_by_tag(tag))

    for track in parsed_prompt['track']:
        if track:
            recommendations.extend(get_recommended_tracks_by_track(track))

    return recommendations

def refine_recommendations(prompt, recommendations):
    query = (
        f"Given the prompt '{prompt}' and the following list of recommendations:\n"
        f"{recommendations}\n\n"
        "Return the recommendations reordered by relevance to the prompt, removing any duplicates or irrelevant tracks. "
        "Return the final list in plain JSON array format, like this: "
        "['Track 1 - Artist 1', 'Track 2 - Artist 2', ...]. "
        "Do not include any commentary, explanations, or text outside the JSON array."
    )

    # Send the request to the model
    payload = {"query": query}
    response = requests.post(DOMAIN, json=payload)

    valid_response = validate_response(response, expected_type="list")

    return valid_response

def run_prompt(prompt):
    parsed_prompt = interpret_prompt(prompt)

    recommendations = get_recommendations(parsed_prompt)

    final_recommendations = refine_recommendations(recommendations, prompt)

    return final_recommendations
