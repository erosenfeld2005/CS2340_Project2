"""
Python file to create and store test cases about the spotify_app
"""

from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone
from django.conf import settings
from django.urls import reverse

from userAuthentication.models import CustomUser
from .models import SpotifyProfile, TemporarySpotifyProfile

class TestTemporarySpotifyProfile(TestCase):
    """
    Tests for the Temporary Spotify Profile
    """
    @patch('spotify_app.models.requests.get')
    def test_fetch_top_tracks(self, mock_get):
        """
        Test fetch top tracks function in model
        :param mock_get: This pretends to get an access code from the API
        and then a corresponding JSON object
        :return: Whether fetch top tracks is working
        """
        # Mock response with valid artist data for both tracks
        mock_response = {
            'items': [
                {'name': 'Song 1', 'artists': [{'name': 'Artist 1'}], 'id': 'track_id_1'},
                {'name': 'Song 2', 'artists': [{'name': 'Artist 2'}], 'id': 'track_id_2'}
            ]
        }
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_response

        temp_profile = TemporarySpotifyProfile()
        tracks = temp_profile.fetch_top_tracks('access_token')

        # Assert that the fetched tracks match the mock data
        self.assertEqual(len(tracks), 2)
        self.assertEqual(tracks[0]['name'], 'Song 1')
        self.assertEqual(tracks[0]['artist'], 'Artist 1')
        self.assertEqual(tracks[1]['name'], 'Song 2')
        self.assertEqual(tracks[1]['artist'], 'Artist 2')

    @patch('spotify_app.models.requests.get')
    def test_fetch_top_artists(self, mock_get):
        """
        Test fetch top artists function in model
        :param mock_get: This pretends to get an access code from the API
        and then a corresponding JSON object
        :return: Whether fetch top artists is working
        """
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
    """
    This holds the tests for the Spotify Profile model
    """
    @patch('spotify_app.models.TemporarySpotifyProfile.fetch_top_tracks')
    @patch('spotify_app.models.TemporarySpotifyProfile.fetch_top_artists')
    def test_save_spotify_profile(self, mock_fetch_top_tracks, mock_fetch_top_artists):
        """
        This tests if the save of spotify profile works correctly
        :param mock_fetch_top_tracks: Pretends to be a return from the API
        :param mock_fetch_top_artists: Pretends to be a return from the API
        :return: Whether save spotify profile works correctly
        """
        # Create a CustomUser instance
        user = CustomUser.objects.create_user(name = "test_name",
                                              username="test_user", password="password")

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
    """
    This holds the tests for spotify login
    """
    def test_spotify_login_redirect(self):
        """
        Tests if spotify login redirects correctly
        :return: Whether spotify login redirect works correctly
        """
        response = self.client.get(reverse('spotify_login'))
        scopes = 'user-top-read'
        auth_url = (
            f"https://accounts.spotify.com/"
            f"authorize?"
            f"client_id={settings.SPOTIFY_CLIENT_ID}"
            f"&response_type=code"
            f"&redirect_uri={settings.SPOTIFY_REDIRECT_URI}&scope={scopes}"
        )

        # Check that it redirects to Spotify's authorization page
        self.assertRedirects(response, auth_url,
                             fetch_redirect_response=False)
                        # Update with actual redirect URL if needed


class TestSpotifyCallbackView(TestCase):
    """
    This holds the tests for spotify callback view
    """
    @patch('spotify_app.views.exchange_code_for_token')
    @patch('spotify_app.views.TemporarySpotifyProfile.fetch_top_tracks')
    @patch('spotify_app.views.TemporarySpotifyProfile.fetch_top_artists')
    def test_spotify_callback_success(self,
                                      mock_fetch_artists,
                                      mock_fetch_tracks,
                                      mock_exchange_token):
        """
        Tests a successful spotify callback view
        :param mock_fetch_artists: A mock return from the API
        :param mock_fetch_tracks:  A mock return from the API
        :param mock_exchange_token:  A mock return from the API
        :return: True if successful spotify callback view is working and
            redirecting to summary.html
        """

        # Log the user in
        self.client.login(username='testuser', password='password')

        # Mock the exchange of the code for a valid access token
        mock_exchange_token.return_value = ('valid_token', 'valid_refresh_token')

        # Mock fetching top tracks and artists
        mock_fetch_tracks.return_value = None  # Simulate successful fetch
        mock_fetch_artists.return_value = None

        # Simulate callback with a valid authorization code
        response = self.client.get(reverse('spotify_callback'), {'code': 'valid_code'})

        # Check if the response is a redirect to 'summary' (the page after success)
        self.assertRedirects(response, reverse('loading'))

        # Check that the TemporarySpotifyProfile was created
        temp_profile = TemporarySpotifyProfile.objects.first()
        self.assertIsNotNone(temp_profile)

        # Ensure the profile data was fetched (mocked methods)
        mock_fetch_tracks.assert_called_once_with('valid_token')
        mock_fetch_artists.assert_called_once_with('valid_token')

        # Check that the temporary_profile_id is stored in the session
        self.assertIn('temporary_profile_id', self.client.session)
        self.assertEqual(self.client.session['temporary_profile_id'], temp_profile.id)

    @patch('spotify_app.views.requests.post')
    def test_spotify_callback_failure(self, mock_post):
        """
        Tests a failed spotify callback view
        :param mock_post: An invalid code
        :return: True if failed spotify callback view is redirecting to error.html
        """
        mock_post.return_value.json.return_value = {'error': 'invalid_request'}

        response = self.client.get(reverse('spotify_callback'), {'code': 'invalid_code'})

        # Check that the response contains the error message
        self.assertContains(response, 'No access token returned')
        self.assertTemplateUsed(response, 'spotify_app/error.html')

class TestSaveSpotifyProfileView(TestCase):
    """
    Tests Saved Spotify Profile View (History)
    """
    def setUp(self):
        """
        Checks setup of a temp profile and user
        :return: Nothing
        """
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
        """
        Tests that the spotify profile saves and redirects correctly
        :return: True if save spotify profile is working
        """
        # Send a POST request with the temporary_profile_id to save the Spotify profile
        response = self.client.post(reverse('save_spotify_profile'), {
            'temporary_profile_id': self.temp_profile.id
        })

        # Ensure the response redirects to the history page
        self.assertRedirects(response, reverse('history'))

        # Check that a SpotifyProfile was created for the logged-in user
        self.assertTrue(SpotifyProfile.objects.filter(user=self.user).exists())

class TestSpotifyCallbackErrorHandling(TestCase):
    """
    Test spotify_callback's error handling
    """
    def test_spotify_callback_no_code(self):
        """
        Test how spotify callback works if the authorization code doesn't work
        :return: True if we get a "Authorization failed" on error.html
        """
        response = self.client.get(reverse('spotify_callback'))
        self.assertContains(response, "Authorization failed.", status_code=200)
        self.assertTemplateUsed(response, 'spotify_app/error.html')

class TestDisplaySummaryContentErrorHandling(TestCase):
    """
    Test if you can display the spotify summary without a temporary profile id
    """
    def test_display_summary_content_missing_profile(self):
        """
        Test if you can display the spotify summary without a temporary profile id
        :return: True if we get the error page and an error of no temp id
        """
        response = self.client.get(reverse('summary'))
        self.assertContains(response, "No temporary profile ID found in session.")
        self.assertTemplateUsed(response, 'spotify_app/error.html')

class TestSaveSpotifyProfileInvalidMethod(TestCase):
    """
    Test how the save spotify profile method works with an invalid request method
    """
    def setUp(self):
        """
        Just set up a user and log them in
        :return: Nothing
        """
        self.user = CustomUser.objects.create_user(username='test_user', password='test_pass')
        self.client.force_login(self.user)

    def test_save_spotify_profile_invalid_method(self):
        """
        Test saved spotify profile with an invalid request method
        :return: True if the request method was invalid
        """
        response = self.client.get(reverse('save_spotify_profile'))
        self.assertContains(response, "Invalid request method.")
        self.assertTemplateUsed(response, 'spotify_app/error.html')

class TestDisplaySavedSummaryContentErrorHandling(TestCase):
    """
    Test display saved summary content's error handling
    """
    def setUp(self):
        """
        Set up user and force log them in
        :return: Nothing
        """
        self.user = CustomUser.objects.create_user(username='test_user', password='test_pass')
        self.client.force_login(self.user)

    def test_display_saved_summary_content_invalid_profile(self):
        """
        Test if you can display saved summary content with an invalid profile
        :return: True if they didn't find the given profile
        """
        invalid_created_at = timezone.now()  # Timestamp unlikely to match any profile
        response = self.client.get(reverse('saved_summary', args=[invalid_created_at]))
        self.assertContains(response, "Profile not found for the given timestamp.")
        self.assertTemplateUsed(response, 'spotify_app/error.html')

class TestDeleteProfileUnauthorizedAccess(TestCase):
    """
    Test how deleting a profile works if you are the wrong user
    """
    def setUp(self):
        """
        Just sets up multiple users
        :return: Nothing
        """
        self.user1 = CustomUser.objects.create_user(username='user1', password='test_pass')
        self.user2 = CustomUser.objects.create_user(username='user2', password='test_pass')
        self.profile = SpotifyProfile.objects.create(user=self.user2)

    def test_delete_profile_unauthorized_access(self):
        """
        Test how deleting a profile works if you are the wrong user
        :return: True if there is an error
        """
        self.client.force_login(self.user1)
        response = self.client.post(reverse('delete_profile', args=[self.profile.id]))
        self.assertEqual(response.status_code, 404)

# class TestLoadingView(TestCase):
#     """
#     Tests for the loading view
#     """
#
#     def setUp(self):
#         """
#         Set up a temporary profile and user session
#         """
#         self.temp_profile = TemporarySpotifyProfile.objects.create(
#             top_songs=['Song 1', 'Song 2'],
#             top_five_songs=['Song 1', 'Song 2', 'Song 3', 'Song 4', 'Song 5'],
#             top_five_artists=['Artist 1', 'Artist 2', 'Artist 3', 'Artist 4', 'Artist 5'],
#             vibe_data={'mood': 'happy'},
#             genre_data={'pop': 2, 'rock': 3},
#         )
#         session = self.client.session
#         session['temporary_profile_id'] = self.temp_profile.id
#         session.save()
#
#     def test_loading_page_renders_correct_template(self):
#         """
#         Test that the loading page renders correctly for standard requests
#         """
#         response = self.client.get(reverse('loading'))
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'spotify_app/loading.html')
#
#     def test_loading_page_with_no_profile(self):
#         """
#         Test behavior when no profile is in session
#         """
#         self.client.session.flush()  # Clear the session
#         response = self.client.get(reverse('loading'))
#         self.assertTemplateUsed(response, 'spotify_app/error.html')
#         self.assertContains(response, 'No profile found.')
#
#     def test_loading_ajax_polling_ready(self):
#         """
#         Test AJAX polling returns 'ready' when data is ready
#         """
#         with patch.object(TemporarySpotifyProfile, 'is_data_ready', return_value=True):
#             response = self.client.get(
#                 reverse('loading'),
#                 HTTP_X_REQUESTED_WITH='XMLHttpRequest'  # Simulate AJAX
#             )
#             self.assertEqual(response.status_code, 200)
#             self.assertJSONEqual(response.content, {'ready': True})
#
#     def test_loading_ajax_polling_not_ready(self):
#         """
#         Test AJAX polling returns 'not ready' when data is not ready
#         """
#         with patch.object(TemporarySpotifyProfile, 'is_data_ready', return_value=False):
#             response = self.client.get(
#                 reverse('loading'),
#                 HTTP_X_REQUESTED_WITH='XMLHttpRequest'  # Simulate AJAX
#             )
#             self.assertEqual(response.status_code, 200)
#             self.assertJSONEqual(response.content, {'ready': False})
#
#     def test_loading_ajax_no_profile(self):
#         """
#         Test AJAX polling with no profile in session
#         """
#         self.client.session.flush()  # Clear the session
#         response = self.client.get(
#             reverse('loading'),
#             HTTP_X_REQUESTED_WITH='XMLHttpRequest'
#         )
#         self.assertEqual(response.status_code, 400)
#         self.assertJSONEqual(response.content, {'ready': False, 'error': 'No profile found.'})
