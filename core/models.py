from django.db import models

class PermisoDummy(models.Model):
    class Meta:
        permissions = [
            # Permisos para mostrar el menú
            ("ver_menu_lista_usuarios", "Puede ver el menú Lista de Usuarios"),
            ("ver_menu_crear_usuario", "Puede ver el menú Crear Usuario"),
            ("ver_menu_asignar_permisos", "Puede ver el menú Roles y Permisos"),

            # Permisos para acciones (botones)
            ("puede_crear_usuario", "Puede crear usuarios"),
            ("puede_editar_usuario", "Puede editar usuarios"),
            ("puede_eliminar_usuario", "Puede eliminar usuarios"),
        ]
