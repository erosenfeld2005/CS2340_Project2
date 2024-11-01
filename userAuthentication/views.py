"""
This function creates the user functionality for the login and signup
"""
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.contrib import messages  # Import messages for feedback
from spotifywrapped import views as spotiftyWrappedViews
from .forms import SignupForm
# Create your views here.
def signup(request):
    """
    Redirects to the signup
    :param request: holds what request the user is making
    :return: the new render request
    """
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(spotiftyWrappedViews.dashboard)
    else:
        form = SignupForm()  # Ensure this initializes a new form
    return render(request, 'userAuthentication/signup.html', {'form': form})




def login_view(request):
    """
    Redirects to the login
    :param request: holds the request that the user is making
    :return: the logged in render request
    """
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect(spotiftyWrappedViews.dashboard)
            messages.error(request, "Invalid username or password.")
        else:
            # When form is invalid, we can add error messages and also return the form
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()  # If it's a GET request, create a new form

    return render(request, 'userAuthentication/login.html',
                  {'form': form})  # Ensure the form is passed back

def spotify_login(request):
    """
    Redirects them to spotify login
    :param request: holds the request that the user is making
    :return: the spotify login render request
    """
    return render(request, 'spotify_callback')  # Ensure this matches the location
