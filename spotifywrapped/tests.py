import os
import asyncio
from django.test import SimpleTestCase
from spotifywrapped.asgi import application


class ASGITest(SimpleTestCase):
    def test_asgi_application(self):
        self.assertTrue(callable(application))

    def test_asgi_application_initialization(self):
        # Create mock receive and send functions to simulate ASGI
        async def mock_receive():
            # Return a message with the required 'type' key
            return {"type": "http.request", "method": "GET", "path": "/"}

        async def mock_send(message):
            # Here you can print or log the response to check if the app sends the expected response
            pass

        # Run the ASGI app with mock receive/send
        scope = {"type": "http", "path": "/", "method": "GET"}
        receive = mock_receive
        send = mock_send

        # Simulate an ASGI call to the application
        async def run_asgi():
            await application(scope, receive, send)

        loop = asyncio.get_event_loop()
        task = loop.create_task(run_asgi())

        # Run the task until completion
        loop.run_until_complete(task)

        # Ensure there were no exceptions during the initialization
        self.assertIsNone(task.exception())

    def test_django_settings_module(self):
        # Ensure the DJANGO_SETTINGS_MODULE is set correctly
        self.assertEqual(os.environ.get('DJANGO_SETTINGS_MODULE'), 'spotifywrapped.settings')
