import requests
from django.conf import settings
from django.shortcuts import redirect, render
from requests.auth import HTTPBasicAuth
import logging

logger = logging.getLogger(__name__)
logging.disable(logging.CRITICAL)

def spotify_login(request):
    scopes = 'user-top-read'
    auth_url = (
        f"https://accounts.spotify.com/authorize?"
        f"client_id={settings.SPOTIFY_CLIENT_ID}&response_type=code"
        f"&redirect_uri={settings.SPOTIFY_REDIRECT_URI}&scope={scopes}"
    )
    return redirect(auth_url)

def spotify_callback(request):
    code = request.GET.get("code")
    if not code:
        return render(request, 'spotify_app/error.html', {"message": "Authorization failed."})

    access_token, refresh_token = exchange_code_for_token(code)

    if not access_token:
        return render(request, 'spotify_app/error.html', {"message": "No access token returned."})

    request.session['access_token'] = access_token
    request.session['refresh_token'] = refresh_token

    return fetch_user_top_data(request)

def exchange_code_for_token(code):
    token_url = "https://accounts.spotify.com/api/token"
    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": settings.SPOTIFY_REDIRECT_URI,
    }
    auth = HTTPBasicAuth(settings.SPOTIFY_CLIENT_ID, settings.SPOTIFY_CLIENT_SECRET)
    response = requests.post(token_url, data=payload, auth=auth)

    if response.status_code != 200:
        logger.error(f"Token request failed: {response.text}")
        return None, None

    response_data = response.json()
    access_token = response_data.get("access_token")
    refresh_token = response_data.get("refresh_token")

    return access_token, refresh_token

def fetch_user_top_data(request):
    access_token = request.session.get('access_token')

    if not access_token:
        return render(request, 'spotify_app/error.html', {"message": "No access token available."})

    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}

    # Fetch top 50 tracks
    top_tracks_url = "https://api.spotify.com/v1/me/top/tracks"
    top_tracks_response = requests.get(top_tracks_url, headers=headers, params={"limit": 50})
    top_tracks_data = top_tracks_response.json()

    # Extract top songs
    top_songs = [
        {"name": track["name"], "artist": track["artists"][0]["name"]}
        for track in top_tracks_data.get("items", [])
    ]

    # Fetch top 50 artists
    top_artists_url = "https://api.spotify.com/v1/me/top/artists"
    top_artists_response = requests.get(top_artists_url, headers=headers, params={"limit": 50})
    top_artists_data = top_artists_response.json()

    # Extract top artists
    top_artists = [
        {"name": artist["name"], "genres": artist["genres"]}
        for artist in top_artists_data.get("items", [])
    ]

    # Store top songs and artists in session
    request.session['top_songs'] = top_songs
    request.session['top_artists'] = top_artists

    return redirect('display_top_songs')  # Redirect to the display songs view

def display_top_songs(request):
    top_songs = request.session.get('top_songs')

    if not top_songs:
        return render(request, 'spotify_app/error.html', {"message": "No top songs found in session."})

    return render(request, 'spotify_app/top_song.html', {
        "top_songs": top_songs
    })

def display_top_artists(request):
    top_artists = request.session.get('top_artists')

    if not top_artists:
        return render(request, 'spotify_app/error.html', {"message": "No top artists found in session."})

    return render(request, 'spotify_app/top_artists.html', {
        "top_artists": top_artists
    })

def determine_top_genre(request):
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
