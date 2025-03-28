from django.contrib import admin
from django.urls import path
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.login_view, name='login'),
    path('home/', views.home_view, name='home'),
    path('usuarios/', views.manage_users_view, name='lista_usuarios'),
    path('usuarios/crear/', views.create_user_view, name='crear_usuario'),
    path('usuarios/editar/<int:pk>/', views.edit_user_view, name='editar_usuario'),
    path('usuarios/eliminar/<int:pk>/', views.delete_user_view, name='eliminar_usuario'),
    path('permisos/asignar/', views.asignar_permisos_view, name='asignar_permisos'),  # 👈 agrega esta
    path('logout/', views.logout_view, name='logout'),

]

