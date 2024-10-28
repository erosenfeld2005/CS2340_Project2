from .models import CustomUser
from django import forms
from django.contrib.auth.forms import UserCreationForm

class SignupForm(UserCreationForm):
    email = forms.EmailField(max_length=200, help_text='Required')
    name = forms.CharField(max_length=150, required=True, help_text='Required')  # Add name as required

    class Meta:
        model = CustomUser
        fields = ('username', 'name', 'email', 'password1', 'password2')
