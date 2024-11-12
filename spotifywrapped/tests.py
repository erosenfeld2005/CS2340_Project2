import os
import asyncio
from django.test import SimpleTestCase
from spotifywrapped.asgi import application

class ASGITest(SimpleTestCase):
    def test_asgi_application(self):
        # Ensure the ASGI application is callable
        self.assertTrue(callable(application))

    def test_asgi_application_initialization(self):
        # Create mock receive and send functions to simulate ASGI
        async def mock_receive():
            # Return a message with the required 'type' key
            return {"type": "http.request"}

        async def mock_send(message):
            pass

        # Run the ASGI app with mock receive/send
        scope = {"type": "http", "path": "/"}  # Ensure a valid scope is provided
        receive = mock_receive
        send = mock_send

        # Simulate an ASGI call to the application
        async def run_asgi():
            await application(scope, receive, send)

        loop = asyncio.get_event_loop()
        task = loop.create_task(run_asgi())
        loop.run_until_complete(task)
        self.assertIsNone(task.exception())  # Ensure no exceptions during initialization

    def test_django_settings_module(self):
        # Ensure the DJANGO_SETTINGS_MODULE is set correctly
        self.assertEqual(os.environ.get('DJANGO_SETTINGS_MODULE'), 'spotifywrapped.settings')