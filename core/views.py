import datetime

from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Permission
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

User = get_user_model()

MANAGED_PERMISSION_CODENAMES = (
    'ver_menu_lista_usuarios',
    'ver_menu_crear_usuario',
    'ver_menu_asignar_permisos',
    'puede_crear_usuario',
    'puede_editar_usuario',
    'puede_eliminar_usuario',
    'acceso_bi_financiero',
    'acceso_bi_operaciones',
    'acceso_bi_cait',
    'acceso_bi_siniestralidad',
)

PERMISSION_CATEGORIES = (
    {
        'key': 'menus_usuarios',
        'label': 'Menus de usuarios',
        'description': 'Permisos para mostrar opciones dentro del menu de administracion.',
        'codenames': (
            'ver_menu_lista_usuarios',
            'ver_menu_crear_usuario',
            'ver_menu_asignar_permisos',
        ),
    },
    {
        'key': 'acciones_usuarios',
        'label': 'Acciones sobre usuarios',
        'description': 'Permisos para crear, editar o eliminar cuentas.',
        'codenames': (
            'puede_crear_usuario',
            'puede_editar_usuario',
            'puede_eliminar_usuario',
        ),
    },
    {
        'key': 'dashboards_bi',
        'label': 'Dashboards BI',
        'description': 'Accesos a los modulos de inteligencia de negocio.',
        'codenames': (
            'acceso_bi_financiero',
            'acceso_bi_operaciones',
            'acceso_bi_cait',
            'acceso_bi_siniestralidad',
        ),
    },
)


def _managed_permissions():
    return Permission.objects.filter(
        content_type__app_label='core',
        codename__in=MANAGED_PERMISSION_CODENAMES,
    ).order_by('name')


def _group_permissions_by_category(permission_qs):
    permissions_by_codename = {permission.codename: permission for permission in permission_qs}
    grouped_permissions = []

    for category in PERMISSION_CATEGORIES:
        category_permissions = [
            permissions_by_codename[codename]
            for codename in category['codenames']
            if codename in permissions_by_codename
        ]

        if category_permissions:
            grouped_permissions.append({
                'key': category['key'],
                'label': category['label'],
                'description': category['description'],
                'permissions': category_permissions,
            })

    return grouped_permissions


def _selected_permission_field(accion):
    return 'permisos_asignados' if accion == 'remover' else 'permisos_disponibles'


def _selected_safe_codenames(request, accion):
    raw_codenames = request.POST.getlist(_selected_permission_field(accion))
    return [codename for codename in raw_codenames if codename in MANAGED_PERMISSION_CODENAMES]


def _redirect_to_permission_editor(usuario_id=None):
    url = reverse('asignar_permisos')
    if usuario_id:
        return redirect(f'{url}?usuario={usuario_id}')
    return redirect(url)


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')

        return render(request, 'login.html', {'error': 'Credenciales incorrectas'})

    return render(request, 'login.html')


@login_required
def home_view(request):
    today = datetime.date.today()
    return render(request, 'home.html', {
        'usuario': request.user.username,
        'today_date': today.strftime('%d/%m/%Y'),
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
    usuarios = User.objects.all().order_by('username')
    return render(request, 'lista_usuarios.html', {
        'usuarios': usuarios,
        'permisos': permisos,
    })


@login_required
@permission_required('core.puede_crear_usuario', raise_exception=True)
def create_user_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        is_staff = request.POST.get('is_staff') == 'on'

        if not username or not email or not password:
            messages.error(request, 'Todos los campos son obligatorios.')
        elif User.objects.filter(username__iexact=username).exists():
            messages.error(request, 'El nombre de usuario ya existe.')
        elif User.objects.filter(email__iexact=email).exists():
            messages.error(request, 'El correo electrónico ya está registrado.')
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.is_staff = is_staff
            user.save(update_fields=['is_staff'])
            messages.success(request, 'Usuario creado con éxito.')
            return redirect('lista_usuarios')

    return render(request, 'crear_usuario.html')


@login_required
@permission_required('core.puede_editar_usuario', raise_exception=True)
def edit_user_view(request, pk):
    usuario = get_object_or_404(User, pk=pk)

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        is_staff = request.POST.get('is_staff') == 'on'

        if not username or not email:
            messages.error(request, 'Nombre de usuario y correo son obligatorios.')
        elif User.objects.exclude(pk=usuario.pk).filter(username__iexact=username).exists():
            messages.error(request, 'El nombre de usuario ya existe.')
        elif User.objects.exclude(pk=usuario.pk).filter(email__iexact=email).exists():
            messages.error(request, 'El correo electrónico ya está registrado.')
        else:
            usuario.username = username
            usuario.email = email
            usuario.is_staff = is_staff

            try:
                with transaction.atomic():
                    usuario.save()
            except IntegrityError:
                messages.error(request, 'No fue posible actualizar el usuario con esos datos.')
            else:
                messages.success(request, 'Usuario actualizado correctamente.')
                return redirect('lista_usuarios')

    return render(request, 'editar_usuario.html', {'usuario': usuario})


@login_required
@permission_required('core.puede_eliminar_usuario', raise_exception=True)
def delete_user_view(request, pk):
    usuario = get_object_or_404(User, pk=pk)

    if request.method == 'POST':
        if usuario.pk == request.user.pk:
            messages.error(request, 'No puedes eliminar tu propio usuario mientras tienes la sesión iniciada.')
            return redirect('lista_usuarios')

        usuario.delete()
        messages.success(request, 'Usuario eliminado correctamente.')
        return redirect('lista_usuarios')

    return render(request, 'eliminar_usuario.html', {'usuario': usuario})


@login_required
@permission_required('core.ver_menu_asignar_permisos', raise_exception=True)
def asignar_permisos_view(request):
    usuarios = User.objects.all().order_by('username')
    permisos = _managed_permissions()

    usuario_seleccionado = None
    permisos_asignados = []
    permisos_disponibles = []

    source = request.POST if request.method == 'POST' else request.GET
    usuario_id = source.get('usuario')
    accion = source.get('accion')

    if usuario_id:
        usuario_seleccionado = get_object_or_404(User, id=usuario_id)

    if request.method == 'POST':
        if not usuario_seleccionado:
            messages.error(request, 'Selecciona un usuario antes de modificar permisos.')
            return _redirect_to_permission_editor()

        permisos_seleccionados = _selected_safe_codenames(request, accion)

        if not permisos_seleccionados:
            messages.warning(request, 'No se seleccionaron permisos válidos.')
            return _redirect_to_permission_editor(usuario_seleccionado.id)

        if accion == 'asignar':
            permisos_a_asignar = permisos.filter(codename__in=permisos_seleccionados)
            usuario_seleccionado.user_permissions.add(*permisos_a_asignar)
            messages.success(request, f'Permisos asignados a {usuario_seleccionado.username}.')
            return _redirect_to_permission_editor(usuario_seleccionado.id)

        if accion == 'remover':
            permisos_a_remover = permisos.filter(codename__in=permisos_seleccionados)
            usuario_seleccionado.user_permissions.remove(*permisos_a_remover)
            messages.success(request, f'Permisos removidos de {usuario_seleccionado.username}.')
            return _redirect_to_permission_editor(usuario_seleccionado.id)

        messages.error(request, 'Acción de permisos no válida.')
        return _redirect_to_permission_editor(usuario_seleccionado.id)

    if usuario_seleccionado:
        permisos_asignados = usuario_seleccionado.user_permissions.filter(
            content_type__app_label='core',
            codename__in=MANAGED_PERMISSION_CODENAMES,
        ).order_by('name')
        permisos_disponibles = permisos.exclude(id__in=permisos_asignados.values('id'))

    return render(request, 'asignar_permisos.html', {
        'usuarios': usuarios,
        'usuario_seleccionado': usuario_seleccionado,
        'permisos_asignados': permisos_asignados,
        'permisos_disponibles': permisos_disponibles,
        'permisos_asignados_agrupados': _group_permissions_by_category(permisos_asignados),
        'permisos_disponibles_agrupados': _group_permissions_by_category(permisos_disponibles),
    })


@login_required
@permission_required('core.acceso_bi_financiero', raise_exception=True)
def powerbi_financiero_view(request):
    return render(request, 'bi_financiero.html')


@login_required
@permission_required('core.acceso_bi_operaciones', raise_exception=True)
def powerbi_dashboard_view(request):
    return render(request, 'bi_operaciones.html')


@login_required
@permission_required('core.acceso_bi_cait', raise_exception=True)
def powerbi_CAIT_view(request):
    return render(request, 'bi_CAIT.html')


@login_required
@permission_required('core.acceso_bi_siniestralidad', raise_exception=True)
def powerbi_siniestralidad_view(request):
    return render(request, 'bi_siniestralidad.html')


def custom_404_view(request, exception):
    return render(request, '404.html', {
        'request_path': request.path,
    }, status=404)
