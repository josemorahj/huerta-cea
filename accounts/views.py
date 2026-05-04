from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from .models import User


@require_http_methods(['GET', 'POST'])
def register_view(request):
    """HU-U1: Registro de usuario con rol voluntario por defecto."""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        apellido = request.POST.get('apellido', '').strip()
        email = request.POST.get('email', '').strip().lower()
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')
        telefono = request.POST.get('telefono', '').strip()

        errores = []
        if not all([nombre, apellido, email, username, password]):
            errores.append('Todos los campos obligatorios deben estar completos.')
        if password != password2:
            errores.append('Las contrasenas no coinciden.')
        if len(password) < 6:
            errores.append('La contrasena debe tener al menos 6 caracteres.')
        if User.objects.filter(email=email).exists():
            errores.append('Este correo electronico ya esta registrado.')
        if User.objects.filter(username=username).exists():
            errores.append('Este nombre de usuario ya esta en uso.')

        if errores:
            for e in errores:
                messages.error(request, e)
            return render(request, 'accounts/register.html', {
                'nombre': nombre, 'apellido': apellido, 'email': email,
                'username': username, 'telefono': telefono,
            })

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=nombre,
            last_name=apellido,
            telefono=telefono,
            rol='voluntario',
        )
        login(request, user)
        messages.success(request, f'Bienvenido {nombre}! Tu cuenta fue creada exitosamente.')
        return redirect('home')

    return render(request, 'accounts/register.html')


@require_http_methods(['GET', 'POST'])
def login_view(request):
    """HU-U2: Inicio de sesion con validacion de credenciales."""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Bienvenido de nuevo, {user.first_name or user.username}.')
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('home')
        else:
            messages.error(request, 'Credenciales incorrectas. Intenta de nuevo.')

    return render(request, 'accounts/login.html')


@require_http_methods(['POST'])
def logout_view(request):
    """Cierre de sesion (solo POST para CSRF)."""
    logout(request)
    messages.success(request, 'Has cerrado sesion correctamente.')
    return redirect('accounts:login')


def home_view(request):
    """Redirige segun rol si esta autenticado, sino al login."""
    if request.user.is_authenticated:
        if request.user.rol == 'admin':
            return redirect('dashboard:home')
        return redirect('activities:list')
    return redirect('accounts:login')