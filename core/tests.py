from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.test import override_settings
from django.urls import reverse


@override_settings(
    SECURE_SSL_REDIRECT=False,
    SESSION_COOKIE_SECURE=False,
    CSRF_COOKIE_SECURE=False,
)
class CoreViewsTests(TestCase):
    def setUp(self):
        self.user_model = get_user_model()

    def create_user(self, username, email, password='Password123!'):
        return self.user_model.objects.create_user(
            username=username,
            email=email,
            password=password,
        )

    def grant_permissions(self, user, *codenames):
        permissions = Permission.objects.filter(
            content_type__app_label='core',
            codename__in=codenames,
        )
        user.user_permissions.add(*permissions)

    def test_login_view_redirects_home_with_valid_credentials(self):
        self.create_user('login_user', 'login@example.com')

        response = self.client.post(reverse('login'), {
            'username': 'login_user',
            'password': 'Password123!',
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('home'))

    def test_create_user_does_not_grant_admin_access_by_default(self):
        manager = self.create_user('creator', 'creator@example.com')
        self.grant_permissions(manager, 'puede_crear_usuario')
        self.client.force_login(manager)

        response = self.client.post(reverse('crear_usuario'), {
            'username': 'nuevo',
            'email': 'nuevo@example.com',
            'password': 'Password123!',
        })

        created_user = self.user_model.objects.get(username='nuevo')

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('lista_usuarios'))
        self.assertFalse(created_user.is_staff)

    def test_edit_user_rejects_duplicate_username(self):
        editor = self.create_user('editor', 'editor@example.com')
        existing = self.create_user('existente', 'existente@example.com')
        target = self.create_user('objetivo', 'objetivo@example.com')
        self.grant_permissions(editor, 'puede_editar_usuario')
        self.client.force_login(editor)

        response = self.client.post(reverse('editar_usuario', args=[target.pk]), {
            'username': existing.username,
            'email': target.email,
        })

        target.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(target.username, 'objetivo')

    def test_delete_user_cannot_delete_current_session_user(self):
        manager = self.create_user('deleter', 'deleter@example.com')
        self.grant_permissions(manager, 'puede_eliminar_usuario')
        self.client.force_login(manager)

        response = self.client.post(reverse('eliminar_usuario', args=[manager.pk]))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('lista_usuarios'))
        self.assertTrue(self.user_model.objects.filter(pk=manager.pk).exists())

    def test_assign_permissions_uses_post_and_filters_unmanaged_permissions(self):
        manager = self.create_user('permadmin', 'permadmin@example.com')
        target = self.create_user('target', 'target@example.com')
        self.grant_permissions(manager, 'ver_menu_asignar_permisos')
        self.client.force_login(manager)

        self.client.get(reverse('asignar_permisos'), {
            'usuario': target.pk,
            'accion': 'asignar',
            'permisos_disponibles': ['acceso_bi_financiero'],
        })
        target = self.user_model.objects.get(pk=target.pk)

        self.assertFalse(target.has_perm('core.acceso_bi_financiero'))

        response = self.client.post(reverse('asignar_permisos'), {
            'usuario': target.pk,
            'accion': 'asignar',
            'permisos_disponibles': ['acceso_bi_financiero', 'add_user'],
        })
        target = self.user_model.objects.get(pk=target.pk)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f"{reverse('asignar_permisos')}?usuario={target.pk}")
        self.assertTrue(target.has_perm('core.acceso_bi_financiero'))
        self.assertFalse(target.has_perm('auth.add_user'))

    def test_permission_editor_groups_permissions_by_category(self):
        manager = self.create_user('roleadmin', 'roleadmin@example.com')
        target = self.create_user('grouped', 'grouped@example.com')
        self.grant_permissions(manager, 'ver_menu_asignar_permisos')
        self.client.force_login(manager)

        response = self.client.get(reverse('asignar_permisos'), {
            'usuario': target.pk,
        })

        self.assertContains(response, 'Menus de usuarios')
        self.assertContains(response, 'Acciones sobre usuarios')
        self.assertContains(response, 'Dashboards BI')
        self.assertContains(response, 'Puede ver y acceder a BI Siniestralidad')

    def test_unknown_route_uses_custom_404_template(self):
        response = self.client.get('/powerbi/financitero/')

        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')
        self.assertContains(response, 'Esta ruta se perdio en el camino', status_code=404)

    def test_powerbi_financiero_requires_permission(self):
        user = self.create_user('viewer', 'viewer@example.com')
        self.client.force_login(user)

        response = self.client.get(reverse('powerbi_financiero'))

        self.assertEqual(response.status_code, 403)

    def test_powerbi_siniestralidad_requires_permission(self):
        user = self.create_user('siniestralidad', 'siniestralidad@example.com')
        self.client.force_login(user)

        forbidden_response = self.client.get(reverse('powerbi_siniestralidad'))
        self.assertEqual(forbidden_response.status_code, 403)

        self.grant_permissions(user, 'acceso_bi_siniestralidad')
        allowed_response = self.client.get(reverse('powerbi_siniestralidad'))
        self.assertEqual(allowed_response.status_code, 200)
