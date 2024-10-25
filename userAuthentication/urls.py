# userAuthentication/urls.py
from django.urls import path
from . import views  # Make sure you have this line


urlpatterns = [
    path("signup/", views.signup, name="signup"),
    path("login/", views.login_view, name="login"),
]
