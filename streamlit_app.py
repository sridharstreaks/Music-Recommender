import streamlit as st
import pandas as pd
import pickle
import requests

# Load data and similarity from pickle files
mini = pickle.load(open('mini.pkl','rb'))
similarity = pickle.load(open('similarity_mini.pkl','rb'))

def search_musicbrainz(artist, song_title):
    base_url = "https://musicbrainz.org/ws/2/"
    search_url = f"{base_url}recording/"

    # Set up parameters for the search
    params = {
        'query': f'artist:"{artist}" AND recording:"{song_title}"',
        'fmt': 'json',
        'limit': 1  # Limit the result to only one recording
    }

    # Make the request to the MusicBrainz API
    response = requests.get(search_url, params=params)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()

        # Check if there are any recordings in the response
        if 'recordings' in data:
            recordings = data['recordings']

            # Print details for the top recording found
            if recordings:
                recording = recordings[0]
                title = recording.get('title', 'N/A')
                artist_name = ', '.join(artist['name'] for artist in recording.get('artist-credit', []))
                release_date = recording.get('first-release-date', 'N/A')
                genre = recording.get('genre', 'N/A')

                print(f"Title: {title}")
                print(f"Artist: {artist_name}")
                print(f"Release Date: {release_date}")
                print(f"Genre: {genre}")
                print(f"ID: {recording['id']}")

                # Get album art from Deezer
                album_art_url = get_deezer_album_art(artist, song_title)
                if album_art_url:
                    print(f"Album Art: {album_art_url}")
                else:
                    print("No album art found.")

                print("\n-----\n")
            else:
                print("No recordings found.")
        else:
            print("No recordings found.")
    else:
        print(f"Error: {response.status_code} - {response.text}")

def get_deezer_album_art(artist, track):
    base_url = "https://api.deezer.com/search"
    
    # Set up parameters for Deezer album art search
    params = {
        'q': f'artist:"{artist}" track:"{track}"',
        'limit': 1
    }
    
    # Make the request to Deezer API
    response = requests.get(base_url, params=params)
    
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        data = response.json()
        
        # Check if there are any results
        if 'data' in data and data['data']:
            return data['data'][0]['album']['cover_big']
    return None

# Get unique song names for the select box
unique_song_names = sorted(set(mini.title))

# Recommender Function
def recommender(song_title):
    idx = mini[mini['title'] == song_title].index[0]
    distances = sorted(list(enumerate(similarity[idx])), reverse=True, key=lambda x: x[1])

    recommended_songs = []
    for idx, distance in distances[1:5]:
        recommended_song = {
            'title': mini.iloc[idx]['title'],
            'artist': mini.iloc[idx]['artist']
        }
        recommended_songs.append(recommended_song)

    return recommended_songs

 

# Streamlit app
def main():
    st.title("Music Recommender App")

    # Sidebar with user input using a select box
    st.sidebar.header("Music Recommender by Streaks")
    st.sidebar.markdown("Select a song title from the list and click the 'Recommend' button to get music recommendations.")

    song_title = st.sidebar.selectbox("Select a song title:", unique_song_names)
    recommend_button = st.sidebar.button("Recommend")

    # Display welcome page if no song title provided
    if not song_title or not recommend_button:
        return

    # Display recommendations when the 'Recommend' button is clicked
    recommendations = recommender(song_title)

    # Display recommendations
    st.header("Top Recommendations:")
    for recommendation in recommendations:
        st.subheader(f"{recommendation['title']} by {recommendation['artist']}")
        search_musicbrainz(recommendation['artist'], recommendation['title'])
        album_art_url = get_deezer_album_art(recommendation['artist'], recommendation['title'])
        if album_art_url:
            st.image(album_art_url, caption=f"Album Art for {recommendation['title']}")
        else:
            st.warning("No album art found.")

        # Display release date and genre
        st.write(f"Release Date: {recommendation.get('release_date', 'N/A')}")
        st.write(f"Genre: {recommendation.get('genre', 'N/A')}")

        st.markdown("---")  # Separator

if __name__ == "__main__":
    main()
