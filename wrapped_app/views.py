from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import status
from rest_framework import response
from rest_framework.response import Response
from requests import Request, post
from django.http import HttpResponse, HttpResponseRedirect
from .credentials import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI
from .extras import *


# Create your views here.
class AuthenticationUrl(APIView):
    def get(self, request, format = None):
        #Currently, I'm only putting in the scopes that this tutorial uses.
        #Later, we will need to change these to get whatever functionalities we actually need
        scopes = "user-read-currently-playing user-read-playback-state user-modify-playback-state"
        url = Request('GET', 'http://accounts.spotify.com/authorize', params = {
            'scopes': scopes,
            'response_type': 'code',
            'redirect_uri': REDIRECT_URI,
            'client_id': CLIENT_ID,
        }).prepare().url
        return HttpResponseRedirect(url)

def spotify_redirect(request, format = None):
    code = request.GET.get('code')
    error = request.GET.get('error')

    if error:
        return HttpResponse(f"Error: {error}", status=400)

    response = post('https://accounts.spotify.com/api/token', {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
    }).json()

    # Check the response status code
    #if response.status_code != 200:
    #    return HttpResponse(f"Error: {response.content.decode()}", status=response.status_code)  # Return the error response

    access_token = response.get('access_token')
    refresh_token = response.get('refresh_token')
    expires_in = response.get('expires_in')
    token_type = response.get('token_type')

    authKey = request.session.session_key
    if not request.session.exists(authKey):
        request.session.create()
        authKey = request.session.session_key
    create_or_update_tokens(
        session_id = authKey,
        access_token = access_token,
        refresh_token = refresh_token,
        expires_in = expires_in,
        token_type = token_type
    )

    #This creates an url that redirects to song details for a song that is currently playing
    redirect_url = f"http://127.0.0.1:8000/spotify/current-song?key={authKey}"
    return HttpResponseRedirect(redirect_url)

class CheckAuthentication(APIView):
    def get(self, request, format = None):
        key = self.request.session.session_key
        if not self.request.session.exists(key):
            self.request.session.create()
            key = request.session.session_key

        auth_status = is_spotify_authenticated(key)

        #Will redirect to the song credentials
        if auth_status:
            redirect_url = f"http://127.0.0.1:8000/spotify/current-song?key={key}"
            return HttpResponseRedirect(redirect_url)
        else:
            #Will redirect to authentication
            redirect_url = "http://127.0.0.1:8000/spotify/auth-url"
            return HttpResponseRedirect(redirect_url)

class CurrentSong(APIView):
    kwarg = 'key'
    def get(self, request, format = None):
        key = request.GET.get(self.kwarg)
        token = Token.objects.filter(user = key)
        print(token)

        #Creating an endpoint
        endpoint = "player/currently-playing"
        response = spotify_redirect(key, endpoint)

        if "error" in response or "item" not in response:
            return Response({}, status = status.HTTP_204_NO_CONTENT)

        item = response.get('item')
        progress = response.get('progress_ms')
        is_playing = response.get("is_playing")
        duration = item.get('duration_ms')
        song_id = item.get('id')
        title = item.get("name")
        album_cover = item.get("album").get("images")[0].get("url")

        artists = ""
        for i, artists in enumerate(item.get("artists")):
            if i > 0:
                artists += ", "
            name = artists.get("name")
            artists += name

        song = {
            'id' : song_id,
            'title' : title,
            'artist' : artists,
            'duration' : duration,
            'time' : progress,
            'album_cover' : album_cover,
            'is_playing' : is_playing,
        }
        print(song)
        return Response(song, status = status.HTTP_200_OK)