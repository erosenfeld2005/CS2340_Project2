"""
Python file that holds how user interacts with spotify_wrapped section
"""
# views.py
from django.shortcuts import render, redirect
from django.conf import settings
from requests.auth import HTTPBasicAuth
import requests
from .models import SpotifyProfile


def spotify_login(request):
    """
    Function that redirects to the login/authorization page
    :return: redirect to the code page
    """
    scopes = 'user-top-read'
    auth_url = (
        f"https://accounts.spotify.com/authorize?"
        f"client_id={settings.SPOTIFY_CLIENT_ID}&response_type=code"
        f"&redirect_uri={settings.SPOTIFY_REDIRECT_URI}&scope={scopes}"
    )
    return redirect(auth_url)


def spotify_callback(request):
    """
    Function that redirects to the top_songs page if it successfully gets the access token
    :param request: Request from the redirected URL
    :return: The appropriate redirect to the top songs page if it successfully gets the access token
    """
    code = request.GET.get("code")
    if not code:
        return render(request, 'spotify_app/error.html', {"message": "Authorization failed."})

    access_token = exchange_code_for_token(code)[0]
    if not access_token:
        return render(request, 'spotify_app/error.html', {"message": "No access token returned."})

    profile = SpotifyProfile.objects.get_or_create(user=request.user)[0]
    profile.fetch_top_tracks(access_token)
    profile.fetch_top_artists(access_token)

    return redirect('summary')


def exchange_code_for_token(code):
    """
    Function that exchanges a authorization code for an access token
    :param code: authorization code
    :return: access token and refresh token
    """
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
    """
    Function that displays the top songs page
    :param request: Redirect input
    :return: the appropriate page
    """
    profile = SpotifyProfile.objects.get(user=request.user)
    if not profile.top_songs:
        return render(request, 'spotify_app/error.html', {"message": "No top songs found."})

    return render(request, 'spotify_app/top_song.html', {"top_songs": profile.top_songs})


def display_music_vibes(request):
    """
    Function that displays the music vibes page
    :param request: Redirect input
    :return: the appropriate page
    """
    profile = SpotifyProfile.objects.get(user=request.user)
    if not profile.vibe_data:
        return render(request, 'spotify_app/error.html', {"message": "No vibe data found."})

    return render(request, 'spotify_app/music_vibes.html', {"vibe_data": profile.vibe_data})


def display_summary_content(request):
    """
    Function that displays the top artists page
    :param request: Redirect input
    :return: the appropriate page
    """
    profile = SpotifyProfile.objects.get(user=request.user)
    if not profile.top_five_artists:
        return render(request, 'spotify_app/error.html', {"message": "No top artists found."})
    if not profile.top_songs:
        return render(request, 'spotify_app/error.html', {"message": "No top songs found."})

    return render(request, 'summary.html', {"top_five_artists":
                                                                profile.top_five_artists,
                                            "top_five_songs": profile.top_five_songs})
    # return render(request, 'summary.html', {"top_five_artists":
    #                                             profile.top_five_artists})


def display_top_genres(request):
    """
    Function that displays the top genres page
    :param request: Redirect input
    :return: the appropriate page
    """
    profile = SpotifyProfile.objects.get(user=request.user)
    top_genres = list(profile.genre_data.items())  # Convert dictionary to list of tuples
    return render(request, 'summary.html', {"top_genres": top_genres})


def history(request):
    """
    Render the user's wrapped history.

    :param request: The HTTP request object.
    :return: The rendered history.html page.
    """
    return render(request, 'history.html')