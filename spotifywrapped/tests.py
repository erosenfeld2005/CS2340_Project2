"""
Python file to create and store test cases about the spotifywrapped app
"""
import os

from django.test import SimpleTestCase
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages

from spotifywrapped.asgi import application
from spotifywrapped.wsgi import application



class WSGITest(SimpleTestCase):
    """
    Tests the WSGI setup
    """
    def test_wsgi_application(self):
        """
        Test if the WSGI application is callable
        :return: Whether the WSGI application is callable
        """
        self.assertTrue(callable(application))

    def test_django_settings_module(self):
        """
        Ensure the DJANGO_SETTINGS_MODULE is set correctly
        :return: Whether the DJANGO_SETTINGS_MODULE is set
        """
        self.assertEqual(os.environ.get('DJANGO_SETTINGS_MODULE'), 'spotifywrapped.settings')

class ASGITest(SimpleTestCase):
    """
    Tests the ASGI setup
    """
    def test_asgi_application(self):
        """
        Test if the ASGI application is callable
        :return: Whether the ASGI application is callable
        """
        self.assertTrue(callable(application))


class WrappedViewsTest(TestCase):
    """
    Tests that check the functionality of spotify_wrapped views.py
    """
    @classmethod
    def setUpTestData(cls):
        """
        Create a user for testing
        :return: Nothing
        """
        cls.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpassword'
        )

    def test_landing_page(self):
        """
        Test that the landing page loads correctly
        :return:
        """
        response = self.client.get(reverse('landing'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'landing.html')

    def test_dashboard_view_logged_in(self):
        """
        Test that dashboard view works when logged in
        :return: True if renders redirect dashboard.html correctly
        """
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard.html')

    def test_dashboard_view_not_logged_in(self):
        """
        Test that the dashboard view doesn't load if logged in
        :return: Test that dashboard view redirects to login.html
        """
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/dashboard/')

    def test_account_settings_view_logged_in(self):
        """
        Test that account settings renders correctly when logged in
        :return: True if account_settings.html renders correctly
        """
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('account_settings'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'deletion/account_settings.html')

    def test_contact_developers_view(self):
        """
        Test the contact developers view
        :return: True if contact_developers.html renders correctly
        """
        response = self.client.get(reverse('contact_developers'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'contact_developers.html')

    def test_submit_feedback_view_post(self):
        """
        Test the render of submit feedback view post
        :return: True if the response goes through contact_developers
        """
        response = self.client.post(reverse('submit_feedback'), {
            'name': 'Test User',
            'email': 'test@example.com',
            'message': 'This is a test message.'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('contact_developers'))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "Thank you for your feedback!")

    # def test_loading_view(self):
    #     """
    #     Test that the loading view
    #     :return: True if renders loading.html
    #     """
    #     response = self.client.get(reverse('loading'))
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, 'loading.html')

    def test_history_view_logged_in(self):
        """
        Test that logged-in users redirect to the history.html page
        :return: True if redirected to history.html
        """
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('history'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'history.html')

    def test_history_view_not_logged_in(self):
        """
        Test that anonymous users are redirected to the login page with the next parameter
        :return: True if this redircts to the login page
        """
        response = self.client.get(reverse('history'))
        self.assertRedirects(response, f'{reverse("login")}?next={reverse("history")}')

    def test_confirm_delete_account_view_logged_in(self):
        """
        Test that confirming a deleted account renders corrected when logged in
        :return: True if confirm deleted accout view redirects to confirm_delete_account.html
        """
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('confirm_delete_account'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'deletion/confirm_delete_account.html')

    def test_account_deleted_view_logged_in(self):
        """
        Test that account deleted redirects correctly when you are logged in
        :return: True if you are redirected to account_deleted.html
        """
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('account_deleted'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'deletion/account_deleted.html')

    def test_delete_account_confirmed_view_post(self):
        """
        Test that delete account goes to the landing page
        :return: True if we redirect to the landing page
        """
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(reverse('delete_account'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('landing'))
