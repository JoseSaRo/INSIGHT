from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User, Permission
from django.contrib import messages
import datetime

User = get_user_model()

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'login.html', {'error': 'Credenciales incorrectas'})
    return render(request, 'login.html')

@login_required
def home_view(request):
    today = datetime.date.today()
    return render(request, 'home.html', {
        'usuario': request.user.username,
        'today_date': today.strftime("%d/%m/%Y")
    })

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
@permission_required('core.ver_menu_lista_usuarios', raise_exception=True)
def manage_users_view(request):
    permisos = {
        'puede_editar_usuario': request.user.has_perm('core.puede_editar_usuario'),
        'puede_eliminar_usuario': request.user.has_perm('core.puede_eliminar_usuario'),
        'puede_crear_usuario': request.user.has_perm('core.puede_crear_usuario'),
    }
    usuarios = User.objects.all()
    return render(request, 'lista_usuarios.html', {
        'usuarios': usuarios,
        'permisos': permisos
    })

@login_required
@permission_required('core.puede_crear_usuario', raise_exception=True)
def create_user_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'El nombre de usuario ya existe.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'El correo electrónico ya está registrado.')
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.is_staff = True
            user.save()
            messages.success(request, 'Usuario creado con éxito.')
            return redirect('lista_usuarios')

    return render(request, 'crear_usuario.html')

@login_required
@permission_required('core.puede_editar_usuario', raise_exception=True)
def edit_user_view(request, pk):
    usuario = get_object_or_404(User, pk=pk)

    if request.method == 'POST':
        usuario.username = request.POST.get('username')
        usuario.email = request.POST.get('email')
        usuario.is_staff = True if request.POST.get('is_staff') == 'on' else False
        usuario.save()
        messages.success(request, 'Usuario actualizado correctamente.')
        return redirect('lista_usuarios')

    return render(request, 'editar_usuario.html', {'usuario': usuario})

@login_required
@permission_required('core.puede_eliminar_usuario', raise_exception=True)
def delete_user_view(request, pk):
    usuario = get_object_or_404(User, pk=pk)

    if request.method == 'POST':
        usuario.delete()
        messages.success(request, 'Usuario eliminado correctamente.')
        return redirect('lista_usuarios')

    return render(request, 'eliminar_usuario.html', {'usuario': usuario})

@login_required
@permission_required('core.ver_menu_asignar_permisos', raise_exception=True)
def asignar_permisos_view(request):
    usuarios = User.objects.all()

    codename_permisos = [
        "ver_menu_lista_usuarios",
        "ver_menu_crear_usuario",
        "ver_menu_asignar_permisos",
        "puede_crear_usuario",
        "puede_editar_usuario",
        "puede_eliminar_usuario",
    ]

    permisos = Permission.objects.filter(codename__in=codename_permisos)

    usuario_seleccionado = None
    permisos_asignados = []
    permisos_disponibles = []

    usuario_id = request.GET.get('usuario')
    accion = request.GET.get('accion')
    permisos_seleccionados = request.GET.getlist(
        'permisos_asignados' if accion == 'remover' else 'permisos_disponibles')

    if usuario_id:
        usuario_seleccionado = User.objects.get(id=usuario_id)

        if accion == 'asignar' and permisos_seleccionados:
            permisos_a_asignar = Permission.objects.filter(codename__in=permisos_seleccionados)
            usuario_seleccionado.user_permissions.add(*permisos_a_asignar)
            messages.success(request, f"Permisos asignados a {usuario_seleccionado.username}.")
        elif accion == 'remover' and permisos_seleccionados:
            permisos_a_remover = Permission.objects.filter(codename__in=permisos_seleccionados)
            usuario_seleccionado.user_permissions.remove(*permisos_a_remover)
            messages.success(request, f"Permisos removidos de {usuario_seleccionado.username}.")

    if usuario_seleccionado:
        permisos_asignados = usuario_seleccionado.user_permissions.filter(codename__in=codename_permisos)
        permisos_disponibles = permisos.exclude(id__in=permisos_asignados)

    return render(request, 'asignar_permisos.html', {
        'usuarios': usuarios,
        'usuario_seleccionado': usuario_seleccionado,
        'permisos_asignados': permisos_asignados,
        'permisos_disponibles': permisos_disponibles,
    })
