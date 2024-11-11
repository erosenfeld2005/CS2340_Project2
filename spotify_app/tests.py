"""
Python file to create and store test cases
"""
from django.test import TestCase

from unittest.mock import patch
from django.utils import timezone

from userAuthentication.models import CustomUser
from .models import SpotifyProfile, TemporarySpotifyProfile
from django.conf import settings
import requests
from django.urls import reverse

class TestTemporarySpotifyProfile(TestCase):
    @patch('spotify_app.models.requests.get')
    def test_fetch_top_tracks(self, mock_get):
        # Include 'id' for each track as required by calculate_vibe_data
        mock_response = {
            'items': [
                {'name': 'Song 1', 'artist': 'Artist 1', 'id': 'track_id_1'},
                {'name': 'Song 2', 'artist': 'Artist 2', 'id': 'track_id_2'}
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
    def test_save_spotify_profile(self, mock_fetch_top_tracks, mock_fetch_top_artists):
        # Create a CustomUser instance
        user = CustomUser.objects.create_user(name = "test_name", username="test_user", password="password")

        # Create a TemporarySpotifyProfile instance
        temp_profile = TemporarySpotifyProfile.objects.create(
            top_songs = ["Top Song 1"],
            top_five_songs = ["Top Five Song 1"],
            top_five_artists = ["Top Five Artists 1"],
            vibe_data = ["vibe data 1"],
            genre_data = ["genre data 1"],
        )

        # Create a SpotifyProfile instance and assign the user and temp_profile
        saved_profile = SpotifyProfile.objects.create(
            user= user,
            top_songs=temp_profile.top_songs,
            top_five_songs=temp_profile.top_five_songs,
            top_five_artists=temp_profile.top_five_artists,
            vibe_data=temp_profile.vibe_data,
            genre_data=temp_profile.genre_data,
            created_at=timezone.now(),
        )

        # Save the instance to the database
        saved_profile.save()

        # Add assertions to check that the profile was saved correctly
        self.assertEqual(saved_profile.user.username, "test_user")
        self.assertEqual(saved_profile.top_songs, temp_profile.top_songs)

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
        self.assertRedirects(response, auth_url, fetch_redirect_response=False)  # Update with actual redirect URL if needed


class TestSpotifyCallbackView(TestCase):
    @patch('spotify_app.views.requests.post')
    def test_spotify_callback_success(self, mock_post):
        mock_post.return_value.json.return_value = {'access_token': 'valid_token'}

        # Simulate callback with a valid authorization code
        response = self.client.get(reverse('spotify_callback'), {'code': 'valid_code'})

        # Check that it redirects correctly after successful token exchange
        self.assertRedirects(response, reverse('summary'))

    @patch('spotify_app.views.requests.post')
    def test_spotify_callback_failure(self, mock_post):
        mock_post.return_value.json.return_value = {'error': 'invalid_request'}

        response = self.client.get(reverse('spotify_callback'), {'code': 'invalid_code'})

        # Check that the response contains the error message
        self.assertContains(response, 'Authorization failed.')
        self.assertTemplateUsed(response, 'spotify_app/error.html')


# class TestDisplayTopSongsView(TestCase):
#     @patch('spotify_app.views.TemporarySpotifyProfile.fetch_top_tracks')
#     def test_display_top_songs_with_valid_session(self, mock_fetch_tracks):
#         # Create a TemporarySpotifyProfile object
#         temp_profile = TemporarySpotifyProfile.objects.create(id=1)
#         temp_profile.top_songs = [{'name': 'Song 1'}]
#         temp_profile.save()
#
#         # Mock the fetch_top_tracks method to return top songs
#         mock_fetch_tracks.return_value = temp_profile.top_songs
#
#         # Set session data to simulate a valid session with a temporary profile ID
#         self.client.session['temporary_profile_id'] = temp_profile.id
#         self.client.session.save()  # Ensure session is saved after modification
#
#         # Send the request to the view
#         response = self.client.get(reverse('display_top_songs'))
#
#         # Check that the correct top song is passed to the template
#         self.assertContains(response, 'Song 1')
#
#         # Ensure the correct template is used
#         self.assertTemplateUsed(response, 'spotify_app/top_song.html')

    # def test_display_top_songs_with_invalid_session(self):
    #     # Test behavior when no temporary_profile_id is in the session
    #     response = self.client.get(reverse('display_top_songs'))
    #
    #     # Expect an error page with a 200 status code if session data is missing
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, 'spotify_app/error.html')
    #     self.assertContains(response, "No temporary profile ID found in session.")

# class TestSaveSpotifyProfileView(TestCase):
#     def setUp(self):
#         # Create a user and log them in
#         self.user = CustomUser.objects.create_user(username='test_user', password='test_pass')
#         self.client.force_login(self.user)
#
#         # Create a temporary profile and save its ID in the session
#         self.temp_profile = TemporarySpotifyProfile.objects.create()
#         session = self.client.session
#         session['temporary_profile_id'] = self.temp_profile.id
#         session.save()
#
#     def test_save_spotify_profile_view(self):
#         # Send a POST request to save the Spotify profile
#         response = self.client.post(reverse('save_spotify_profile'))
#
#         # Ensure the response redirects to the history page
#         self.assertRedirects(response, reverse('history'))
#
#         # Check that a SpotifyProfile was created for the logged-in user
#         self.assertTrue(SpotifyProfile.objects.filter(user=self.user).exists())

class TestSaveSpotifyProfileView(TestCase):
    def setUp(self):
        # Create and log in a user
        self.user = CustomUser.objects.create_user(username='test_user', password='test_pass')
        self.client.force_login(self.user)

        # Create a temporary profile
        self.temp_profile = TemporarySpotifyProfile.objects.create(
            top_songs=[{'name': 'Song 1'}],
            top_five_songs=['Song 1', 'Song 2'],
            top_five_artists=['Artist 1', 'Artist 2'],
            vibe_data={'mood': 'happy'},
            genre_data={'genre': 'pop'}
        )

    def test_save_spotify_profile_view(self):
        # Send a POST request with the temporary_profile_id to save the Spotify profile
        response = self.client.post(reverse('save_spotify_profile'), {
            'temporary_profile_id': self.temp_profile.id
        })

        # Ensure the response redirects to the history page
        self.assertRedirects(response, reverse('history'))

        # Check that a SpotifyProfile was created for the logged-in user
        self.assertTrue(SpotifyProfile.objects.filter(user=self.user).exists())