import requests
from django.conf import settings
from django.shortcuts import redirect, render
from requests.auth import HTTPBasicAuth
import logging

logger = logging.getLogger(__name__)


def spotify_login(request):
    # Step 1: Redirect to Spotify authorization page
    scopes = 'user-top-read'
    auth_url = (
        f"https://accounts.spotify.com/authorize?"
        f"client_id={settings.SPOTIFY_CLIENT_ID}&response_type=code"
        f"&redirect_uri={settings.SPOTIFY_REDIRECT_URI}&scope={scopes}"
    )
    return redirect(auth_url)


def spotify_callback(request):
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
    refresh_token = response_data.get("refresh_token")  # Get refresh token if available

    return access_token, refresh_token


def fetch_user_top_tracks(request):
    access_token = request.session.get('access_token')

    if not access_token:
        return render(request, 'spotify_app/error.html', {"message": "No access token available."})

    # Request to get the user's top tracks
    top_tracks_url = "https://api.spotify.com/v1/me/top/tracks"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    top_tracks_response = requests.get(top_tracks_url, headers=headers)

    logger.info(f"Top tracks response status code: {top_tracks_response.status_code}")

    if top_tracks_response.status_code != 200:
        logger.error(f"Failed to retrieve top tracks: {top_tracks_response.text}")
        return render(request, 'spotify_app/error.html', {"message": "Could not retrieve top track."})

    top_tracks_data = top_tracks_response.json()

    # Extract the most listened-to song
    if "items" in top_tracks_data and top_tracks_data["items"]:
        most_listened_song = top_tracks_data["items"][0]["name"]
        artist = top_tracks_data["items"][0]["artists"][0]["name"]
        return render(request, 'spotify_app/top_song.html', {
            "song": most_listened_song,
            "artist": artist,
        })
    else:
        logger.warning("No top tracks found or response format unexpected.")
        return render(request, 'spotify_app/error.html', {"message": "Could not retrieve top track."})
