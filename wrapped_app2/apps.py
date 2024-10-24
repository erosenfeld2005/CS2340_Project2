from django.apps import AppConfig


class WrappedApp2Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'wrapped_app2'
