from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.db.models import ProtectedError

from .models import User
from .forms import UsuarioForm, UsuarioCrearForm


def es_admin(user):
    return user.is_authenticated and getattr(user, 'rol', None) == 'admin'


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


@login_required
def usuario_list_view(request):
    """RF-10: listado de usuarios para gestión por admin."""
    if not es_admin(request.user):
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('home')

    usuarios = User.objects.all().order_by('username')
    return render(request, 'accounts/usuario_list.html', {'usuarios': usuarios})


@login_required
@require_http_methods(['GET', 'POST'])
def usuario_crear_view(request):
    """RF-10: alta de usuario por admin, con rol elegible."""
    if not es_admin(request.user):
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('home')

    if request.method == 'POST':
        form = UsuarioCrearForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuario creado correctamente.')
            return redirect('accounts:usuario_list')
    else:
        form = UsuarioCrearForm()

    return render(request, 'accounts/usuario_form.html', {'form': form, 'modo': 'crear'})


@login_required
@require_http_methods(['GET', 'POST'])
def usuario_editar_view(request, pk):
    """RF-10: edición de usuario existente por admin."""
    if not es_admin(request.user):
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('home')

    usuario = get_object_or_404(User, pk=pk)

    if request.method == 'POST':
        form = UsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuario actualizado correctamente.')
            return redirect('accounts:usuario_list')
    else:
        form = UsuarioForm(instance=usuario)

    return render(request, 'accounts/usuario_form.html', {'form': form, 'modo': 'editar', 'usuario': usuario})


@login_required
@require_http_methods(['POST'])
def usuario_eliminar_view(request, pk):
    """RF-10: eliminación de usuario por admin. No permite autoeliminarse."""
    if not es_admin(request.user):
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('home')

    usuario = get_object_or_404(User, pk=pk)

    if usuario.pk == request.user.pk:
        messages.error(request, 'No puedes eliminar tu propia cuenta.')
        return redirect('accounts:usuario_list')

    try:
        usuario.delete()
        messages.success(request, 'Usuario eliminado correctamente.')
    except ProtectedError:
        messages.error(request, f'No se puede eliminar a {usuario.username}: tiene actividades u otros registros asociados. Desactívalo en su lugar (editar usuario, desmarcar "Activo").')

    return redirect('accounts:usuario_list')