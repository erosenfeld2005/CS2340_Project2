# views.py
from django.shortcuts import render, redirect
from django.conf import settings
from .models import SpotifyProfile
from requests.auth import HTTPBasicAuth
import requests


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

    profile, created = SpotifyProfile.objects.get_or_create(user=request.user)
    profile.fetch_top_tracks(access_token)
    profile.fetch_top_artists(access_token)

    return redirect('display_top_songs')


def exchange_code_for_token(code):
    token_url = "https://accounts.spotify.com/api/token"
    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": settings.SPOTIFY_REDIRECT_URI,
    }
    auth = HTTPBasicAuth(settings.SPOTIFY_CLIENT_ID, settings.SPOTIFY_CLIENT_SECRET)
    response = requests.post(token_url, data=payload, auth=auth, timeout=15)

    if response.status_code == 200:
        response_data = response.json()
        return response_data.get("access_token"), response_data.get("refresh_token")
    return None, None


def display_top_songs(request):
    profile = SpotifyProfile.objects.get(user=request.user)
    if not profile.top_songs:
        return render(request, 'spotify_app/error.html', {"message": "No top songs found."})

    return render(request, 'spotify_app/top_song.html', {"top_songs": profile.top_songs})


def display_music_vibes(request):
    profile = SpotifyProfile.objects.get(user=request.user)
    if not profile.vibe_data:
        return render(request, 'spotify_app/error.html', {"message": "No vibe data found."})

    return render(request, 'spotify_app/music_vibes.html', {"vibe_data": profile.vibe_data})


def display_top_artists(request):
    profile = SpotifyProfile.objects.get(user=request.user)
    if not profile.top_artists_with_images:
        return render(request, 'spotify_app/error.html', {"message": "No top artists found."})

    return render(request, 'spotify_app/top_artists.html', {"top_artists_with_images": profile.top_artists_with_images})


def display_top_genres(request):
    profile = SpotifyProfile.objects.get(user=request.user)
    top_genres = list(profile.genre_data.items())  # Convert dictionary to list of tuples
    return render(request, 'spotify_app/top_genres.html', {"top_genres": top_genres})
