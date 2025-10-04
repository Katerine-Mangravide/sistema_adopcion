from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = "usuarios"

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_adoptante, name='login'),
    path('logout/', views.logout_adoptante, name='logout'),
    path('register/', views.register_adoptante, name='register'),
    path('perfil/', views.ver_perfil, name='perfil'),
    path('perfil/editar/', views.editar_perfil, name='editar_perfil'),
    path('perfil/cambiar-contrasena/', views.cambiar_contrasena, name='cambiar_contrasena'),
    path('perfil/desactivar/', views.desactivar_cuenta, name='desactivar_cuenta'),
    path('perfil/descargar/<str:formato>/', views.descargar_datos, name='descargar_datos'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # 🔑 Password reset (usamos las vistas oficiales de Django con plantillas personalizadas)
    path(
        'password-reset/',
        auth_views.PasswordResetView.as_view(
            template_name="usuarios/password_reset.html",
            email_template_name="usuarios/password_reset_email.html",   # correo
            subject_template_name="usuarios/password_reset_subject.txt" # asunto
        ),
        name='password_reset'
    ),
    path(
        'password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name="usuarios/password_reset_done.html"
        ),
        name='password_reset_done'
    ),
    path(
        'password-reset-confirm/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name="usuarios/password_reset_confirm.html"
        ),
        name='password_reset_confirm'
    ),
    path(
        'password-reset-complete/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name="usuarios/password_reset_complete.html"
        ),
        name='password_reset_complete'
    ),
]
