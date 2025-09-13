from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User

# --- LOGIN ---
def login_adoptante(request):
    if request.method == "POST":
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('usuarios:home')
        messages.error(request, "Usuario o contraseña incorrectos")
    return render(request, 'usuarios/login.html')

# --- LOGOUT ---
def logout_adoptante(request):
    logout(request)
    messages.success(request, "Has cerrado sesión correctamente")
    return redirect('usuarios:login')

# --- REGISTRO ---
def register_adoptante(request):
    if request.method == "POST":
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if password != confirm_password:
            messages.error(request, "Las contraseñas no coinciden")
            return redirect('usuarios:register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "El nombre de usuario ya existe")
            return redirect('usuarios:register')

        if email and User.objects.filter(email=email).exists():
            messages.error(request, "Ya existe un usuario con ese correo")
            return redirect('usuarios:register')

        user = User.objects.create_user(username=username, email=email, password=password)
        messages.success(request, "Registro exitoso. Ahora puedes iniciar sesión")
        return redirect('usuarios:login')

    return render(request, 'usuarios/register.html')

# --- HOME ---
def home(request):
    return render(request, 'usuarios/home.html')