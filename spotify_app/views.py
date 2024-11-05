"""
Python file that holds how user interacts with spotify_wrapped section
"""
# views.py
import requests

from requests.auth import HTTPBasicAuth

from django.conf import settings
from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib.auth import logout

from .models import SpotifyProfile, TemporarySpotifyProfile

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

def signout(request):
    """
    View to sign out and redirect to the landing page
    """
    logout(request)  # Log out the user
    return redirect('landing')  # Redirect to landing after signing out

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

    # Create a TemporarySpotifyProfile instance for the current user
    temp_profile = TemporarySpotifyProfile.objects.create(
        top_songs=[],  # Initialize with empty data or whatever your default is
        top_five_songs=[],
        top_five_artists=[],
        vibe_data=None,  # Initialize as needed
        genre_data={},
        # Note: No user field as per your design
    )

    # Fetch and populate the data into the temporary profile
    temp_profile.fetch_top_tracks(access_token)
    temp_profile.fetch_top_artists(access_token)

    # Optionally, you can store the temporary profile to the session for later retrieval
    request.session['temporary_profile_id'] = temp_profile.id
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
    temp_profile_id = request.session.get('temporary_profile_id')
    # Retrieve the profile ID from the session

    if temp_profile_id:
        try:
            temp_profile = TemporarySpotifyProfile.objects.get(id=temp_profile_id)
            # Get the temporary profile by ID
            if not temp_profile.top_songs:
                return render(request, 'spotify_app/error.html',
                              {"message": "No top songs found."})

            return render(request, 'spotify_app/top_song.html',
                          {"top_songs": temp_profile.top_songs})
        except TemporarySpotifyProfile.DoesNotExist:
            return render(request, 'spotify_app/error.html',
                          {"message": "Temporary profile not found."})
    else:
        return render(request, 'spotify_app/error.html',
                      {"message": "No temporary profile ID found in session."})


def display_music_vibes(request):
    """
    Function that displays the music vibes page using TemporarySpotifyProfile
    :param request: Redirect input
    :return: the appropriate page
    """
    temp_profile_id = request.session.get('temporary_profile_id')
    # Retrieve the profile ID from the session

    if temp_profile_id:
        try:
            temp_profile = TemporarySpotifyProfile.objects.get(id=temp_profile_id)
            # Get the temporary profile by ID
            if not temp_profile.vibe_data:
                return render(request, 'spotify_app/error.html',
                              {"message": "No vibe data found."})

            # Combine both dictionaries into a single context dictionary
            context = {
                "vibe_data": temp_profile.vibe_data,
                "temporary_profile_id": temp_profile_id
            }
            return render(request, 'spotify_app/music_vibes.html', context)
        except TemporarySpotifyProfile.DoesNotExist:
            return render(request, 'spotify_app/error.html',
                          {"message": "Temporary profile not found."})
    else:
        return render(request, 'spotify_app/error.html',
                      {"message": "No temporary profile ID found in session."})


def display_summary_content(request):
    """
    Function that displays the top artists page
    :param request: Redirect input
    :return: the appropriate page
    """
    temp_profile_id = request.session.get('temporary_profile_id')
    # Retrieve the profile ID from the session

    if temp_profile_id:
        try:
            temp_profile = TemporarySpotifyProfile.objects.get(id=temp_profile_id)
            # Get the temporary profile by ID
            if not temp_profile.top_five_artists:
                return render(request, 'spotify_app/error.html',
                              {"message": "No top artists found."})
            if not temp_profile.top_songs:
                return render(request, 'spotify_app/error.html',
                              {"message": "No top songs found."})
            return render(request, 'summary.html', {"top_five_artists":
                                                        temp_profile.top_five_artists,
                                            "top_five_songs": temp_profile.top_five_songs,
                                                    "temp_profile_id": temp_profile_id})
        except TemporarySpotifyProfile.DoesNotExist:
            return render(request, 'spotify_app/error.html',
                          {"message": "Temporary profile not found."})
    else:
        return render(request, 'spotify_app/error.html',
                      {"message": "No temporary profile ID found in session."})

def display_top_genres(request):
    """
    Function that displays the top genres page
    :param request: Redirect input
    :return: the appropriate page
    """
    temp_profile_id = request.session.get('temporary_profile_id')
    # Retrieve the profile ID from the session

    if temp_profile_id:
        try:
            temp_profile = TemporarySpotifyProfile.objects.get(id=temp_profile_id)
            # Get the temporary profile by ID
            if not temp_profile.genre_data:
                return render(request, 'spotify_app/error.html',
                              {"message": "No genre data found."})

            top_genres = list(temp_profile.genre_data.items())
                # Convert dictionary to list of tuples
            return render(request, 'summary.html', {"top_genres": top_genres})

        except TemporarySpotifyProfile.DoesNotExist:
            return render(request, 'spotify_app/error.html',
                          {"message": "Temporary profile not found."})
    else:
        return render(request, 'spotify_app/error.html',
                      {"message": "No temporary profile ID found in session."})

def save_spotify_profile(request):
    """
    Function to save the TemporarySpotifyProfile to the user's SpotifyProfile
    """
    if request.method == 'POST':
        # Retrieve the temporary_profile_id from the POST request
        temporary_profile_id = request.POST.get('temporary_profile_id')

        # Try to get the TemporarySpotifyProfile using the provided ID
        try:
            temp_profile = TemporarySpotifyProfile.objects.get(id=temporary_profile_id)

            # Create a new SpotifyProfile linked to the logged-in user with
            # data from the temporary profile
            SpotifyProfile.objects.create(
                user=request.user,
                top_songs=temp_profile.top_songs,
                top_five_songs = temp_profile.top_five_songs,
                top_five_artists=temp_profile.top_five_artists,
                vibe_data=temp_profile.vibe_data,
                genre_data=temp_profile.genre_data,
                created_at=timezone.now(),
            )
            return redirect('display_saved_profiles')  # Redirect to the saved profiles page
        except TemporarySpotifyProfile.DoesNotExist:
            return render(request, 'spotify_app/error.html',
                          {"message": "Temporary profile not found."})
        except Exception as e:
            # Handle any other exceptions, such as database errors
            return render(request, 'spotify_app/error.html', {"message": str(e)})

        # Handle the case where the request method is not POST
    return render(request, 'spotify_app/error.html', {"message": "Invalid request method."})

def display_saved_profiles(request):
    """
    Function to display saved Spotify profiles
    """
    profiles = request.user.spotify_profiles.all()  # Retrieve all profiles for the logged-in user
    return render(request, 'spotify_app/saved_profiles.html', {'profiles': profiles})
