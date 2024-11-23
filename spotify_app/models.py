"""
Python file where models are created
"""

from django.db import models
import requests

from userAuthentication.models import CustomUser


class TemporarySpotifyProfile(models.Model):
    """
    Model for the Temporary Spotify Profile
    """
    top_songs = models.JSONField(default=list, blank=True)
    top_five_songs = models.JSONField(default=list, blank=True)
    top_five_artists = models.JSONField(default=list, blank=True)
    vibe_data = models.JSONField(default=dict, blank=True, null=True)
    genre_data = models.JSONField(default=dict, blank=True)
    time_range = models.CharField(max_length=100, blank=True, null=True, default="medium_term")

    def fetch_top_tracks(self, access_token, time_range):
        """
        Gathers the top tracks data from the Spotify API.
        :param access_token: user specific token
        :param time_range: generate long, medium or short term wrapped
        :return: The list of top songs
        """
        headers = {"Authorization": f"Bearer {access_token}",
                   "Content-Type": "application/json"}
        top_tracks_url = "https://api.spotify.com/v1/me/top/tracks"
        response = requests.get(top_tracks_url, headers=headers,
                                params={"time_range":time_range,"limit": 50}, timeout=15)
        if response.status_code == 200:
            top_tracks_data = response.json().get("items", [])
            top_tracks = [{
                "name": track.get("name"),
                "artist": track["artists"][0]["name"] if track.get("artists") else "Unknown Artist",
                "popularity": track.get("popularity"),
                "image_url": track["album"]["images"][0]["url"] if track.get("album") and
                                                                   track["album"].get(
                    "images") else None,
                "preview_url": track.get("preview_url")
            } for track in top_tracks_data]
            self.top_songs = top_tracks
            self.calculate_vibe_data(top_tracks_data, headers)  # Update vibe data
            self.time_range = time_range
            self.save()

            #Top Five Songs
            self.top_five_songs = top_tracks[0:5]
            self.save()
            return top_tracks
        return []

    def calculate_vibe_data(self, top_tracks_data, headers):
        """
        Method that calculates the vibe data from the top tracks data.
        :param top_tracks_data: list of top tracks
        :param headers: header data needed by spotify api
        :return: None
        """
        total_danceability, total_valence, total_energy = 0, 0, 0
        for track in top_tracks_data:
            audio_features_url = f"https://api.spotify.com/v1/audio-features/{track['id']}"
            audio_features_response = requests.get(audio_features_url, headers=headers, timeout=15)
            if audio_features_response.status_code == 200:
                audio_features = audio_features_response.json()
                total_danceability += audio_features.get("danceability", 0)
                total_valence += audio_features.get("valence", 0)
                total_energy += audio_features.get("energy", 0)

        count = len(top_tracks_data) or 1
        self.vibe_data = {
            "average_danceability": (total_danceability / count) * 100,
            "average_valence": (total_valence / count) * 100,
            "average_energy": (total_energy / count) * 100,
        }
        self.save()

    def fetch_top_artists(self, access_token, time_range):
        """
        Gathers the top artists data from the Spotify API.
        :param access_token: user specific data
        :param time_range: generate long, medium or short term wrapped
        :return: list of top artists
        """
        ## Pulling from API
        headers = {"Authorization": f"Bearer {access_token}",
                   "Content-Type": "application/json"}
        top_artists_url = "https://api.spotify.com/v1/me/top/artists"
        response = requests.get(top_artists_url, headers=headers,
                                params={"time_range":time_range,"limit": 50}, timeout=15)
        if response.status_code == 200:
            top_artists_data = response.json().get("items", [])
            top_artists = [{
                "name": artist.get("name"),
                "genres": artist.get("genres"),
                "popularity": artist.get("popularity"),
                "image_url": artist["images"][0]["url"] if artist.get("images") else None
            } for artist in top_artists_data]

            #Calculate Genre
            genre_counts = {}
            for artist in top_artists_data:
                for genre in artist.get("genres", []):
                    genre_counts[genre] = genre_counts.get(genre, 0) + 1
            sorted_genres = sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)
            self.genre_data = dict(sorted_genres[:5])  # Store only top 5 genres
            self.save()

            self.top_five_artists = top_artists[0:5]
            self.save()

            return top_artists
        return []

    def is_data_ready(self):
        """
        Method that confirms if all the data has been received and stored from the
        spotify api.
        :return: True if it has and false otherwise
        """
        return all([
            self.top_songs,
            self.top_five_songs,
            self.top_five_artists,
            self.vibe_data is not None,
            self.genre_data,
        ])
class SpotifyProfile(models.Model):
    """
        Model for the Saved Spotify Profile
        """
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='spotify_profiles')
    top_songs = models.JSONField(default=list, blank=True)
    top_five_songs = models.JSONField(default=list, blank=True)
    top_five_artists = models.JSONField(default=list, blank=True)
    vibe_data = models.JSONField(default=dict, blank=True, null=True)
    genre_data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp for when the profile was saved
    time_range = models.CharField(max_length=100, blank=True, null=True, default="medium_term")
