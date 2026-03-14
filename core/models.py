# core/models.py
from django.db import models

class PermisoDummy(models.Model):
    class Meta:
        permissions = [
            # Menú 
            ("ver_menu_lista_usuarios", "Puede ver el menú Lista de Usuarios"),
            ("ver_menu_crear_usuario", "Puede ver el menú Crear Usuario"),
            ("ver_menu_asignar_permisos", "Puede ver el menú Roles y Permisos"),

            # Acciones 
            ("puede_crear_usuario", "Puede crear usuarios"),
            ("puede_editar_usuario", "Puede editar usuarios"),
            ("puede_eliminar_usuario", "Puede eliminar usuarios"),

             # === un solo permiso por BI ===
            ("acceso_bi_financiero", "Puede ver y acceder a BI Financiero"),
            ("acceso_bi_operaciones", "Puede ver y acceder a BI Operaciones"),
            ("acceso_bi_cait", "Puede ver y acceder a BI CAIT"),
        ]
