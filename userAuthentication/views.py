from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate
from .forms import SignupForm
from django.shortcuts import render, redirect
from django.contrib import messages  # Import messages for feedback

# Create your views here.
def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('signup_success')
    else:
        form = SignupForm()
    return render(request, 'userAuthentication/signup.html', {'form': form})



def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('signup_success')  # Redirect to a home page after successful login
            else:
                messages.error(request, "Invalid username or password.")  # Show error message
        else:
            messages.error(request, "Invalid username or password.")  # Show error if form is invalid
    else:
        form = AuthenticationForm()

    return render(request, 'userAuthentication/login.html', {'form': form})


def signup_success(request):
    return render(request, 'signup_sucess.html')  # Ensure this matches the location
