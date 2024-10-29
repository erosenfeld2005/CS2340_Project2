"""
Python file to configure the different apps
"""
from django.apps import AppConfig

class UserauthenticationConfig(AppConfig):
    """
    Configures user authentication
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'userAuthentication'
