import streamlit as st
import requests

DOMAIN = "http://<your_local_ip>:<your_port>"
PROMPT_ERROR = "Sorry, I couldn't understand your request. Please try phrasing it differently!"

def validate_response(response):
    # Try to parse the JSON response and handle potential errors
    try:
        # Check if the response is successful (status code 200)
        if response.status_code == 200:
            # Attempt to parse the JSON content from the response
            model_response = response.json()
            
            # Check if the structure matches what you expect
            if isinstance(model_response, dict) and 'artist' in model_response and 'genre' in model_response and 'tags' in model_response:
                return model_response
            else:
                # If the response doesn't match the expected format, display an error
                st.error("Error: Response structure is incorrect.")
                st.stop()
        else:
            # Handle if the status code is not 200 (success)
            st.error(f"Error: Unable to process the request. Status code: {response.status_code}")
            st.stop()

    except ValueError:
        # If the response isn't valid JSON, catch the ValueError and display an error message
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

    valid_response = validate_response(response)

    # Apply the safe_split function to the artist and genre fields
    valid_response['artist'] = safe_split(response.get('artist', ''))
    valid_response['genre'] = safe_split(response.get('genre', ''))

    return valid_response

def create_api_calls(parsed_prompt):
    api_calls = []
    # get 5 or 10 for each artist, genre, and tag

    if parsed_prompt['artist']:
        for artist in parsed_prompt['artist']:
            api_calls.append(f"")

    if parsed_prompt['genre']:
        for genre in parsed_prompt['genre']:
            api_calls.append(f"")

    if parsed_prompt['tags']:
        for tag in parsed_prompt['tags']:
            api_calls.append(f"")

    return api_calls

def get_recommendations(parsed_prompt):
    api_calls = create_api_calls(parsed_prompt)

    # Loop through the API calls and make requests to the Last.fm API
    recommendations = [] # should be a list of dicts of track info

    for call in api_calls:


    return recommendations

def compare_results_with_prompt(recommendations, parsed_prompt):
    
    return final_recommendations

def run_prompt(prompt):
    parsed_prompt = interpret_prompt(prompt)

    # Step 2: Get recommendations
    try:
        recommendations = get_recommendations(parsed_prompt)
    except Exception as e:
        st.error("Sorry, something went wrong while finding recommendations. Please try again later.")
        st.stop()

    # Step 3: Compare results with the prompt
    try:
        final_recommendations = compare_results_with_prompt(recommendations, prompt)
    except Exception as e:
        st.error("Sorry, something went wrong while finalising your recommendations. Please try again.")
        st.stop()

    return final_recommendations
