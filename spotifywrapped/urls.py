"""
URL configuration for spotifywrapped project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from userAuthentication import views as accounts_views  # Import the views from the accounts app
from . import views
#from django.contrib.auth import views as auth_views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.landing_page, name='landing'),
    path('login/', accounts_views.login_view, name='login'),
    path('accounts/', include('userAuthentication.urls')),
    path('spotify_login/', accounts_views.spotify_login, name='spotify_login'),
    path("spotify/", include("spotify_app.urls")),
    path('dashboard/', views.dashboard, name='dashboard'),
    # path('summary/', views.summary, name='summary'),
    path('account/', views.account_settings, name='account_settings'),
    path('account/confirm_delete/', views.confirm_delete_account, name='confirm_delete_account'),
    path('account/deleted/', views.account_deleted, name='account_deleted'),
    path('account/delete/', views.delete_account_confirmed, name='delete_account'),
    path('history/', views.history, name='history'),
    path('contact_developers/', views.contact_developers, name='contact_developers'),
    path('submit_feedback/', views.submit_feedback, name='submit_feedback'),
    path('loading/', views.loading, name='loading')
]
