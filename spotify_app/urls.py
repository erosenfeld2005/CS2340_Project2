"""
Python file that stores the different url paths that our website can access
"""
from django.urls import path
from . import views

urlpatterns = [
    path("spotifylogin/", views.spotify_login, name="spotify_login"),
    path('error/', views.error_view, name='error'),  # Define the error page URL with the name 'error'
    path("callback/", views.spotify_callback, name="spotify_callback"),
    #path('fetch_data/', views.fetch_user_top_data, name='fetch_user_top_data'),
    #path('display_songs/', views.display_top_songs, name='display_top_songs'),
    path('summary/', views.display_summary_content, name='summary'),
    path('top_genres/', views.display_top_genres, name='top_genres'),
    path('music_vibes/', views.display_music_vibes, name='music_vibes'),
    path('save_profile/', views.save_spotify_profile, name='save_spotify_profile'),
    path('saved_profiles/', views.display_saved_profiles, name='display_saved_profiles'),
    path('signout/', views.signout, name='signout'),
    path('saved_summary/<str:created_at>/', views.display_saved_summary_content,
         name='saved_summary'),
    path('delete_profile/<int:profile_id>/', views.delete_profile, name='delete_profile'),
]
