"""
Python file that stores the different url paths that our website can access
"""
from django.urls import path
from . import views

urlpatterns = [
    path("spotifylogin/", views.spotify_login, name="spotify_login"),
    path("callback/", views.spotify_callback, name="spotify_callback"),
]
