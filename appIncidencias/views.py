from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.urls import reverse
from django.contrib import messages

# Create your views here.
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect(reverse('home')) 
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    return render(request, 'core/login.html')

def home_view(request):
    return render(request, 'core/home.html')

def add_reports(request):
    return render (request, 'core/addReports.html')

def user_managment(request):
    return render (request, 'core/userManagment.html')

def view_reports(request):
    return render (request, 'core/viewReports.html')
