from django.contrib import admin
from django.urls import path, reverse_lazy
from core import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.login_view, name='login'),
    path('home/', views.home_view, name='home'),
    path('usuarios/', views.manage_users_view, name='lista_usuarios'),
    path('usuarios/crear/', views.create_user_view, name='crear_usuario'),
    path('usuarios/editar/<int:pk>/', views.edit_user_view, name='editar_usuario'),
    path('usuarios/eliminar/<int:pk>/', views.delete_user_view, name='eliminar_usuario'),
    path('permisos/asignar/', views.asignar_permisos_view, name='asignar_permisos'),
    path('logout/', views.logout_view, name='logout'),

    path('powerbi/', views.powerbi_dashboard_view, name='powerbi_dashboard'),
    path('powerbi/financiero/', views.powerbi_financiero_view, name='powerbi_financiero'),
    path('powerbi/cait/', views.powerbi_CAIT_view, name='powerbi_CAIT'),

    # ==========================
    #  Rutas para reset password
    # ==========================
    path(
        'password-reset/',
        auth_views.PasswordResetView.as_view(
            template_name='password_reset_form.html',          # 👈 SIN "core/"
            email_template_name='password_reset_email.html',   # 👈
            subject_template_name='password_reset_subject.txt',
            success_url=reverse_lazy('password_reset_done')
        ),
        name='password_reset'
    ),
    path(
        'password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='password_reset_done.html'           # 👈 SIN "core/"
        ),
        name='password_reset_done'
    ),
    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='password_reset_confirm.html',       # 👈
            success_url=reverse_lazy('password_reset_complete')
        ),
        name='password_reset_confirm'
    ),
    path(
        'reset/done/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='password_reset_complete.html'       # 👈
        ),
        name='password_reset_complete'
    ),
]
