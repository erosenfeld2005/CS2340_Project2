import os
import asyncio
from django.test import SimpleTestCase
from spotifywrapped.asgi import application

class ASGITest(SimpleTestCase):
    def test_asgi_application(self):
        self.assertTrue(callable(application))

    def test_django_settings_module(self):
        self.assertEqual(os.environ.get('DJANGO_SETTINGS_MODULE'), 'spotifywrapped.settings')
