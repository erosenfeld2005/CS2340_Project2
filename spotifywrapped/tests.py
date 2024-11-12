import asyncio
from django.test import SimpleTestCase
from spotifywrapped.asgi import application
import os

class ASGITest(SimpleTestCase):
    def test_asgi_application(self):
        # Ensure the ASGI application is callable
        self.assertIsCallable(application)

    def test_asgi_application_initialization(self):
        loop = asyncio.get_event_loop()
        task = loop.create_task(application({}))
        loop.run_until_complete(task)
        self.assertIsNone(task.exception())  # Ensure no exceptions during initialization

    def test_django_settings_module(self):
        # Ensure the DJANGO_SETTINGS_MODULE is set correctly
        self.assertEqual(os.environ.get('DJANGO_SETTINGS_MODULE'), 'spotifywrapped.settings')