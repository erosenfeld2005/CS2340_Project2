"""
Python file that controls redirects and functionality
"""
import requests
from django.conf import settings
from django.shortcuts import redirect, render
from requests.auth import HTTPBasicAuth

def spotify_login(request): # pylint: disable=unused-argument
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
    This method gets the users authorization code, then uses that to get their access token.
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
    request.session['refresh_token'] = refresh_token  # Optional, for token refresh later

    # Fetch user's top tracks
    return fetch_user_top_tracks(request)


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
    response = requests.post(token_url, data=payload, auth=auth, timeout = 15)

    if response.status_code != 200:
        return None, None

    response_data = response.json()
    access_token = response_data.get("access_token")
    refresh_token = response_data.get("refresh_token")  # Get refresh token if available

    return access_token, refresh_token


def fetch_user_top_tracks(request):
    """
    This function fetches the top track of the user
    :param request: Request is used to access the API
    :return: Either an error page or the user's top song and its artist
    """
    access_token = request.session.get('access_token')

    if not access_token:
        return render(request, 'spotify_app/error.html', {"message": "No access token available."})

    # Request to get the user's top tracks
    top_tracks_url = "https://api.spotify.com/v1/me/top/tracks"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    top_tracks_response = requests.get(top_tracks_url, headers=headers, timeout = 15)


    if top_tracks_response.status_code != 200:
        return render(request, 'spotify_app/error.html',
                      {"message": "Could not retrieve top track."})

    top_tracks_data = top_tracks_response.json()

    # Extract the most listened-to song
    if "items" in top_tracks_data and top_tracks_data["items"]:
        most_listened_song = top_tracks_data["items"][0]["name"]
        artist = top_tracks_data["items"][0]["artists"][0]["name"]
        return render(request, 'spotify_app/top_song.html', {
            "song": most_listened_song,
            "artist": artist,
        })
    return render(request, 'spotify_app/error.html',
                    {"message": "Could not retrieve top track."})
