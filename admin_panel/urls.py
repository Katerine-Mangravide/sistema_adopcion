# admin_panel/urls.py
from django.urls import path
from . import views

app_name = "admin_panel"

urlpatterns = [
    path('', views.dashboard, name='dashboard'),

    # Usuarios
    path('usuarios/', views.gestion_usuarios, name='gestion_usuarios'),
    path('usuarios/crear/', views.crear_usuario, name='crear_usuario'),
    path('usuarios/editar/<int:user_id>/', views.editar_usuario, name='editar_usuario'),
    path('usuarios/eliminar/<int:user_id>/', views.eliminar_usuario, name='eliminar_usuario'),

    # Refugios
    path('refugios/', views.gestion_refugios, name='gestion_refugios'),
    path('refugios/crear/', views.crear_refugio, name='crear_refugio'),
    path('refugios/editar/<int:refugio_id>/', views.editar_refugio, name='editar_refugio'),
    path('refugios/eliminar/<int:refugio_id>/', views.eliminar_refugio, name='eliminar_refugio'),

    # Mascotas
    path('mascotas/', views.gestion_mascotas, name='gestion_mascotas'),
    path('mascotas/crear/', views.crear_mascota, name='crear_mascota'),
    path('mascotas/editar/<int:mascota_id>/', views.editar_mascota, name='editar_mascota'),
    path('mascotas/eliminar/<int:mascota_id>/', views.eliminar_mascota, name='eliminar_mascota'),

    # Solicitudes
    path('solicitudes/', views.gestion_solicitudes, name='gestion_solicitudes'),
    path('solicitudes/editar/<int:solicitud_id>/', views.editar_solicitud, name='editar_solicitud'),
    path('solicitudes/eliminar/<int:solicitud_id>/', views.eliminar_solicitud, name='eliminar_solicitud'),
]
