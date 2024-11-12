import os
from django.test import SimpleTestCase
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

