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
        "'artist': [artist1, artist2, ...], "
        "'genre': [genre1, genre2, ...], "
        "'track': [track1, track2, ...], "
        "'tag': [tag1, tag2, ...]"
        "}. "
        "If any information is missing, use an empty list. "
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

    print(f"\nTracks for artist {artist_name}: {data}")

    tracks = []
    if 'toptracks' in data:
        for track in data['toptracks']['track']:
            tracks.append(track['name'])
    return tracks

def get_recommended_tracks_by_artist(artist_name):
    similar_artists = get_similar_artists(artist_name)
    print(f"\nSimilar artists for {artist_name}: {similar_artists}")
    time.sleep(SLEEP)
    all_tracks = []

    for artist in similar_artists:
        tracks = get_tracks_for_artist(artist)
        for track in tracks:
            all_tracks.append((artist, track))
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

    print(f"\nTracks for tag {tag}: {data}")

    tracks = []
    if 'tracks' in data:
        for track in data['tracks']['track']:
            tracks.append((track['artist']['name'], track['name']))
    
    return tracks

def get_recommended_tracks_by_genre(genre):
    params = {
        'method': 'tag.gettoptracks',
        'tag': genre,
        'api_key': API_KEY,
        'format': 'json',
        'limit': 5
    }
    response = requests.get(API_URL, params=params)
    data = validate_lastfm_response(response, expected_keys=['tracks'])

    print(f"\nTracks for genre {genre}: {data}")

    tracks = []
    if 'tracks' in data:
        for track in data['tracks']['track']:
            tracks.append((track['artist']['name'], track['name']))
    
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

    print(f"Tracks similar to {track_name}: {data}")

    tracks = []
    if 'similartracks' in data:
        for track in data['similartracks']['track']:
            tracks.append((track['artist']['name'], track['name']))
    
    return tracks

def get_tags_for_tracks(tracks, max_tags=5):
    """
    Given a list of (artist, track) tuples, return a list of [artist, track, tags] entries.
    Each tags list is limited to `max_tags` items.
    """
    results = []

    for artist, track in tracks:
        params = {
            'method': 'track.gettoptags',
            'artist': artist,
            'track': track,
            'api_key': API_KEY,
            'format': 'json'
        }
        response = requests.get(API_URL, params=params)
        data = validate_lastfm_response(response, expected_keys=['toptags'])

        print(f"\nTags for {artist} - {track}: {data}")

        tags = []
        if 'toptags' in data and 'tag' in data['toptags']:
            for tag in data['toptags']['tag'][:max_tags]:
                if isinstance(tag, dict) and 'name' in tag:
                    tags.append(tag['name'])

        results.append([artist, track, tags])

    return results

def get_recommendations(parsed_prompt):
    recommendations = []

    for artist in parsed_prompt['artist']:
        if artist:
            recommendations.extend(get_recommended_tracks_by_artist(artist))

    for tag in parsed_prompt['tag']:
        if tag:
            recommendations.extend(get_recommended_tracks_by_tag(tag))
        time.sleep(SLEEP)  # To avoid hitting API rate limits
    
    for genre in parsed_prompt.get('genre', []):
        if genre:
            recommendations.extend(get_recommended_tracks_by_genre(genre))
        time.sleep(SLEEP)

    for track in parsed_prompt.get('track', []):
        if track:
            recommendations.extend(get_recommended_tracks_by_track(track))
        time.sleep(SLEEP)

    recommendations = get_tags_for_tracks(recommendations)

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
    start = time.time()

    #parsed_prompt = interpret_prompt(prompt)
    parsed_prompt = json.loads(prompt) # Testing with direct prompt for simplicity

    recommendations = get_recommendations(parsed_prompt)

    # final_recommendations = refine_recommendations(recommendations, prompt)

    end = time.time()
    elapsed = end - start
    print(f"\n⏱️ Elapsed time: {elapsed/60:.4f} minutes")

    #return final_recommendations
    return recommendations # Testing with direct recommendations for simplicity


# Extreme example prompt for testing
# {"artist": ["Radiohead", "Portishead", "Massive Attack"],"genre": ["Alternative Rock", "Trip-Hop", "Electronica"],"tag": ["moody", "experimental", "UK", "1990s", "layered"],"tracks": ["Teardrop", "Karma Police", "Unfinished Sympathy"]}
