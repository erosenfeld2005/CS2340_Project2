"""
Python file that controls redirects and functionality
"""
from django.conf import settings
from django.shortcuts import redirect, render
from requests.auth import HTTPBasicAuth
import requests

def spotify_login(request):  # pylint: disable=unused-argument
    """
    This method redirects login to the authorization page
    :param request: access the spotify API key
    :return: the redirect url
    """
    # Step 1: Redirect to Spotify authorization page
    scopes = 'user-top-read'
    auth_url = (
        f"https://accounts.spotify.com/authorize?"
        f"client_id={settings.SPOTIFY_CLIENT_ID}&response_type=code"
        f"&redirect_uri={settings.SPOTIFY_REDIRECT_URI}&scope={scopes}"
    )
    return redirect(auth_url)

def spotify_callback(request):
    """
    This method gets the user's authorization code, then uses that to get their access token.
    Then it calls the fetch top songs method
    :param request: Used to access the API
    :return: the call to the fetch user top data method
    """
    # Step 2: Get the authorization code from Spotify
    code = request.GET.get("code")
    if not code:
        return render(request, 'spotify_app/error.html', {"message": "Authorization failed."})

    # Step 3: Exchange code for access token
    access_token, refresh_token = exchange_code_for_token(code)

    if not access_token:
        return render(request, 'spotify_app/error.html', {"message": "No access token returned."})

    # Store tokens in session
    request.session['access_token'] = access_token
    request.session['refresh_token'] = refresh_token

    return fetch_user_top_data(request)

def exchange_code_for_token(code):
    """
    Exchanges the user's code for an access token to use the Spotify API
    :param code: Their code
    :return: Their access token and refresh token
    """
    token_url = "https://accounts.spotify.com/api/token"
    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": settings.SPOTIFY_REDIRECT_URI,
    }
    auth = HTTPBasicAuth(settings.SPOTIFY_CLIENT_ID, settings.SPOTIFY_CLIENT_SECRET)
    response = requests.post(token_url, data=payload, auth=auth, timeout=15)

    if response.status_code != 200:
        return None, None

    response_data = response.json()
    access_token = response_data.get("access_token")
    refresh_token = response_data.get("refresh_token")

    return access_token, refresh_token

def fetch_user_top_data(request):
    """
    This function fetches the top tracks of the user and calculates average danceability, valence, and energy
    :param request: Request is used to access the API
    :return: Either an error page or the user's average music vibes
    """
    access_token = request.session.get('access_token')

    if not access_token:
        return render(request, 'spotify_app/error.html', {"message": "No access token available."})

    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}

    # Fetch top 50 tracks
    top_tracks_url = "https://api.spotify.com/v1/me/top/tracks"
    top_tracks_response = requests.get(top_tracks_url, headers=headers, params={"limit": 50}, timeout=15)
    if top_tracks_response.status_code != 200:
        return render(request, 'spotify_app/error.html', {"message": "Could not retrieve top tracks."})

    top_tracks_data = top_tracks_response.json()

    # Calculate average danceability, valence, and energy
    total_danceability = 0
    total_valence = 0
    total_energy = 0
    track_count = len(top_tracks_data.get("items", []))

    for track in top_tracks_data.get("items", []):
        audio_features_url = f"https://api.spotify.com/v1/audio-features/{track['id']}"
        audio_features_response = requests.get(audio_features_url, headers=headers)
        if audio_features_response.status_code == 200:
            audio_features = audio_features_response.json()
            total_danceability += audio_features.get("danceability", 0)
            total_valence += audio_features.get("valence", 0)
            total_energy += audio_features.get("energy", 0)

    average_danceability = total_danceability / track_count if track_count else 0
    average_valence = total_valence / track_count if track_count else 0
    average_energy = total_energy / track_count if track_count else 0

    # Prepare vibe data for rendering
    request.session['vibe_data'] = {
        "average_danceability": average_danceability,
        "average_valence": average_valence,
        "average_energy": average_energy
    }
    return redirect('display_top_songs')
def display_music_vibes(request):
    """
    Display the average danceability, valence, and energy of the user's top songs.
    :param request: User request
    :return: Render the music vibes HTML page
    """
    vibe_data = request.session.get('vibe_data')

    if not vibe_data:
        return render(request, 'spotify_app/error.html', {"message": "No vibe data found in session."})

    return render(request, 'spotify_app/music_vibes.html', {
        "vibe_data": vibe_data
    })

def display_top_songs(request):
    """
    Method to display the top 50 songs of the current user
    :param request: user request
    :return: the top songs html page
    """
    top_songs = request.session.get('top_songs')

    if not top_songs:
        return render(request, 'spotify_app/error.html', {"message": "No top songs found in session."})

    return render(request, 'spotify_app/top_song.html', {
        "top_songs": top_songs
    })

def display_top_artists(request):
    """
    Method to display the top 50 artists of the current user
    :param request: user request
    :return: the top artists html page
    """
    top_artists = request.session.get('top_artists')

    if not top_artists:
        return render(request, 'spotify_app/error.html', {"message": "No top artists found in session."})

    return render(request, 'spotify_app/top_artists.html', {
        "top_artists": top_artists
    })

def determine_top_genre(request):
    """
    Method to display the top 5 genres of the current user
    :param request: user request
    :return: the top genres html page
    """
    top_artists = request.session.get('top_artists', [])
    top_genres = {}

    # Count occurrences of each genre
    for artist in top_artists:
        curr_genres = artist.get("genres", [])
        for genre in curr_genres:
            top_genres[genre] = top_genres.get(genre, 0) + 1

    # Sort genres by count and get the top 5
    sorted_genres = sorted(top_genres.items(), key=lambda x: x[1], reverse=True)
    top_5_genres = sorted_genres[:5]

    # Return or render the result
    return render(request, 'spotify_app/top_genres.html', {
        "top_genres": top_5_genres
    })