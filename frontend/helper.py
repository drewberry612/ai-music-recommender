import streamlit as st
import requests
from dotenv import load_dotenv
import os
import json
import time

load_dotenv()

SLEEP = 0  # Global sleep duration in seconds

DOMAIN = "http://<your_local_ip>:<your_port>"
API_URL = "http://ws.audioscrobbler.com/2.0/"
API_KEY = os.getenv("API_KEY")
PROMPT_ERROR = "Sorry, I couldn't understand your request. Please try phrasing it differently."
API_ERROR = "Sorry, something went wrong while obtaining recommendations. Please try again later."
REFINE_ERROR = "Sorry, something went wrong while finalising your recommendations. Please try again."

# Dictionary of all recommendation metadata
RECOMMENDATION_METADATA = {}

def validate_response(response, expected_type):
    try:
        if response.status_code == 200:
            model_response = response.json()
            if expected_type == "dict":
                if isinstance(model_response, dict) and 'artist' in model_response and 'tags' in model_response:
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

def interpret_prompt(prompt):
    query = (
        f"Given the prompt '{prompt}', extract the key information and return it in this exact structured format: "
        "{"
        "'artist': [artist1, artist2, ...], "
        "'tags': [tag1, tag2, ...]"
        "}. "
        "If any information is missing, use an empty list. "
        "Include any genres you find in the prompt as tags in the 'tags' field. "
        "Return only the structure, no additional commentary or explanation."
    )
    
    # Send the request to the model
    payload = {"query": query}
    response = requests.post(DOMAIN, json=payload)

    valid_response = validate_response(response, expected_type="dict")

    return valid_response

def get_album_cover_url(track):
    # This needs testing properly
    images = track.get('image', [])
    # Try to get the largest available image
    for size in ['extralarge', 'large', 'medium', 'small']:
        for img in images:
            if img.get('size') == size and img.get('#text'):
                return img['#text']
    return ''

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
            tracks.append({
                "track": track['name'],
                "artist": track['artist']['name'],
                "tags": []
            })

            RECOMMENDATION_METADATA[(track['name'], track['artist']['name'])] = {
                "tags": [],
                "album_cover_url": get_album_cover_url(track),
                "track_link_url": track.get('url', '')
            }

    return tracks

def get_recommended_tracks_by_artist(artist_name):
    similar_artists = get_similar_artists(artist_name)
    print(f"\nSimilar artists for {artist_name}: {similar_artists}")
    time.sleep(SLEEP)
    all_tracks = []

    for artist in similar_artists:
        all_tracks.extend(get_tracks_for_artist(artist))
        time.sleep(SLEEP)
    
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
            tracks.append({
                "track": track['name'],
                "artist": track['artist']['name'],
                "tags": []
            })

            RECOMMENDATION_METADATA[(track['name'], track['artist']['name'])] = {
                "tags": [],
                "album_cover_url": get_album_cover_url(track),
                "track_link_url": track.get('url', '')
            }
    
    return tracks

def get_tags_for_tracks(tracks, max_tags=10):
    results = []

    for track_info in tracks:
        artist = track_info['artist']
        track = track_info['track']
        params = {
            'method': 'track.gettoptags',
            'artist': artist,
            'track': track,
            'api_key': API_KEY,
            'format': 'json'
        }
        response = requests.get(API_URL, params=params)
        data = validate_lastfm_response(response, expected_keys=['toptags'])

        tags = []
        if 'toptags' in data and 'tag' in data['toptags']:
            for tag in data['toptags']['tag'][:max_tags]:
                if isinstance(tag, dict) and 'name' in tag:
                    tags.append(tag['name'])

        track_info['tags'] = tags
        RECOMMENDATION_METADATA[(track, artist)]['tags'] = tags

        results.append(track_info)

    return results

def remove_duplicates(recommendations):
    seen = set()
    result = []
    for rec in recommendations:
        key = (rec['track'], rec['artist'])
        if key not in seen:
            seen.add(key)
            result.append(rec)
    return result

def get_recommendations(parsed_prompt):
    recommendations = []

    # Map keys to their corresponding functions
    key_func_map = {
        'artist': get_recommended_tracks_by_artist,
        'tags': get_recommended_tracks_by_tag,
    }

    for key, func in key_func_map.items():
        for item in parsed_prompt.get(key, []):
            if item:
                recommendations.extend(func(item))
            time.sleep(SLEEP)  # To avoid hitting API rate limits

    recommendations = remove_duplicates(recommendations)

    recommendations = get_tags_for_tracks(recommendations)

    return recommendations

def refine_recommendations(prompt, recommendations):
    query = (
        f"Given the prompt '{prompt}' and the following list of recommendations:\n"
        f"{recommendations}\n\n"
        "Return the recommendations reordered by relevance to the prompt, removing any irrelevant tracks. "
        "Return the final list in plain JSON array format, like this: "
        "[('track1', 'artist1'), ('track2', 'artist2'), ...]. "
        "Do not include any commentary, explanations, or text outside the JSON array."
    )

    # Send the request to the model
    payload = {"query": query}
    response = requests.post(DOMAIN, json=payload)

    valid_response = validate_response(response, expected_type="list")

    return valid_response

def run_prompt(prompt):
    start = time.time()

    #parsed_prompt = interpret_prompt(prompt)
    parsed_prompt = json.loads(prompt) # Testing with direct prompt for simplicity

    recommendations = get_recommendations(parsed_prompt)

    #recommendations = refine_recommendations(recommendations, parsed_prompt)

    end = time.time()
    elapsed = end - start
    print(f"\n⏱️ Elapsed time: {elapsed/60:.4f} minutes")

    print(f"\nMetadata: {RECOMMENDATION_METADATA}")

    return recommendations, RECOMMENDATION_METADATA


# Extreme example prompt for testing
# {"artist": ["Radiohead", "Portishead", "Massive Attack"], "tags": ["moody", "experimental", "UK", "1990s", "layered", "Alternative Rock", "Trip-Hop", "Electronica"]}

# {"artist": [], "tags": ["Alternative Rock"]}
