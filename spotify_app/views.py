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
    :return: the call to the fetch top songs method
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
    This function fetches the top track of the user
    :param request: Request is used to access the API
    :return: Either an error page or the user's top song and its artist
    """
    access_token = request.session.get('access_token')

    if not access_token:
        return render(request, 'spotify_app/error.html', {"message": "No access token available."})

    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}

    # Fetch top 50 tracks
    top_tracks_url = "https://api.spotify.com/v1/me/top/tracks"
    top_tracks_response = requests.get(top_tracks_url, headers=headers, params={"limit": 50}, timeout=15)
    if top_tracks_response.status_code != 200:
        return render(request, 'spotify_app/error.html', {"message": "Could not retrieve top track."})

    top_tracks_data = top_tracks_response.json()

    # Extract top songs
    top_songs = [
        {"name": track["name"], "artist": track["artists"][0]["name"]}
        for track in top_tracks_data.get("items", [])
    ]

    # Fetch top 50 artists
    top_artists_url = "https://api.spotify.com/v1/me/top/artists"
    top_artists_response = requests.get(top_artists_url, headers=headers, params={"limit": 50}, timeout=15)
    if top_artists_response.status_code != 200:
        return render(request, 'spotify_app/error.html', {"message": "Could not retrieve top artists."})

    top_artists_data = top_artists_response.json()

    # Extract top artists along with their images
    top_artists = [
        {
            "name": artist["name"],
            "genres": artist["genres"],
            "image": artist["images"][0]["url"] if artist["images"] else None  # Get the first image if available
        }
        for artist in top_artists_data.get("items", [])
    ]

    # Store top songs and artists in session
    request.session['top_songs'] = top_songs
    request.session['top_artists'] = top_artists

    return redirect('display_top_songs')  # Redirect to the display songs view

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
