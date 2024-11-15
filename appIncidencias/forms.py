from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .views import Department

class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Usuario')
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
