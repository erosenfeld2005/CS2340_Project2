"""
Python file to create and store test cases
"""
from django.test import TestCase

from unittest.mock import patch
from .models import SpotifyProfile, TemporarySpotifyProfile
from .views import display_top_songs
from django.conf import settings
import requests
from django.urls import reverse

class TestTemporarySpotifyProfile(TestCase):
    @patch('spotify_app.models.requests.get')
    def test_fetch_top_tracks(self, mock_get):
        mock_response = {
            'items': [
                {'name': 'Song 1', 'artist': 'Artist 1'},
                {'name': 'Song 2', 'artist': 'Artist 2'}
            ]
        }
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_response

        temp_profile = TemporarySpotifyProfile()
        tracks = temp_profile.fetch_top_tracks('access_token')

        self.assertEqual(len(tracks), 2)
        self.assertEqual(tracks[0]['name'], 'Song 1')
        self.assertEqual(tracks[1]['artist'], 'Artist 2')

    @patch('spotify_app.models.requests.get')
    def test_fetch_top_artists(self, mock_get):
        mock_response = {
            'items': [
                {'name': 'Artist 1'},
                {'name': 'Artist 2'}
            ]
        }
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_response

        temp_profile = TemporarySpotifyProfile()
        artists = temp_profile.fetch_top_artists('access_token')

        self.assertEqual(len(artists), 2)
        self.assertEqual(artists[0]['name'], 'Artist 1')
        self.assertEqual(artists[1]['name'], 'Artist 2')

class TestSpotifyProfile(TestCase):
    @patch('spotify_app.models.TemporarySpotifyProfile.fetch_top_tracks')
    @patch('spotify_app.models.TemporarySpotifyProfile.fetch_top_artists')
    def test_save_spotify_profile(self, mock_fetch_artists, mock_fetch_tracks):
        mock_fetch_tracks.return_value = [{'name': 'Song 1', 'artist': 'Artist 1'}]
        mock_fetch_artists.return_value = [{'name': 'Artist 1'}]

        temp_profile = TemporarySpotifyProfile()
        # Normally save_spotify_profile would be called in views.py
        saved_profile = SpotifyProfile(user="test_user", temp_profile=temp_profile)
        saved_profile.save()

        self.assertEqual(saved_profile.user, "test_user")
        self.assertEqual(len(saved_profile.top_songs), 1)
        self.assertEqual(saved_profile.top_songs[0]['name'], 'Song 1')
        self.assertEqual(saved_profile.top_artists[0]['name'], 'Artist 1')

class TestSpotifyLoginView(TestCase):
    def test_spotify_login_redirect(self):
        response = self.client.get(reverse('spotify_login'))
        scopes = 'user-top-read'
        auth_url = (
            f"https://accounts.spotify.com/authorize?"
            f"client_id={settings.SPOTIFY_CLIENT_ID}&response_type=code"
            f"&redirect_uri={settings.SPOTIFY_REDIRECT_URI}&scope={scopes}"
        )

        # Check that it redirects to Spotify's authorization page
        self.assertRedirects(response, auth_url)  # Update with actual redirect URL if needed


class TestSpotifyCallbackView(TestCase):
    @patch('spotify_app.views.requests.post')
    def test_spotify_callback_success(self, mock_post):
        mock_post.return_value.json.return_value = {'access_token': 'valid_token'}

        # Simulate callback with a valid authorization code
        response = self.client.get(reverse('spotify_callback'), {'code': 'valid_code'})

        # Check that it redirects correctly after successful token exchange
        self.assertRedirects(response, reverse('display_top_songs'))

    @patch('spotify_app.views.requests.post')
    def test_spotify_callback_failure(self, mock_post):
        mock_post.return_value.json.return_value = {'error': 'invalid_request'}

        response = self.client.get(reverse('spotify_callback'), {'code': 'invalid_code'})

        # Check for redirection to the error page if the API call fails
        self.assertRedirects(response, reverse('error'))


class TestDisplayTopSongsView(TestCase):
    @patch('spotify_app.views.TemporarySpotifyProfile.fetch_top_tracks')
    def test_display_top_songs_with_valid_session(self, mock_fetch_tracks):
        mock_fetch_tracks.return_value = [{'name': 'Song 1'}]

        # Set session data
        self.client.session['temporary_profile_id'] = 1

        response = self.client.get(reverse('display_top_songs'))

        # Check that the top songs are correctly passed to the template
        self.assertContains(response, 'Song 1')

    def test_display_top_songs_with_invalid_session(self):
        # Test behavior when no temporary_profile_id is in the session
        response = self.client.get(reverse('display_top_songs'))

        # Expect an error page if session data is missing
        self.assertRedirects(response, reverse('error'))

class TestSaveSpotifyProfileView(TestCase):
    def test_save_spotify_profile(self):
        # Assuming a temporary profile exists in the session
        temp_profile = TemporarySpotifyProfile.objects.create()
        self.client.session['temporary_profile_id'] = temp_profile.id

        response = self.client.post(reverse('save_spotify_profile'))

        # Ensure the profile is saved and redirects to the history page
        self.assertRedirects(response, reverse('history'))
        self.assertTrue(SpotifyProfile.objects.filter(user='test_user').exists())