"""
Python file that stores the different url paths that our website can access
"""
from django.urls import path
from . import views

urlpatterns = [
    path("spotifylogin/", views.spotify_login, name="spotify_login"),
    path("callback/", views.spotify_callback, name="spotify_callback"),
    #path('fetch_data/', views.fetch_user_top_data, name='fetch_user_top_data'),
    path('display_songs/', views.display_top_songs, name='display_top_songs'),
    path('display_artists/', views.display_top_artists,name='display_top_artists'),
    path('top_genres/', views.display_top_genres, name='top_genres'),
    path('music_vibes/', views.display_music_vibes, name='music_vibes'),
]
