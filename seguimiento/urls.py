from django.urls import path
from . import views

app_name = 'seguimiento'

urlpatterns = [
    path('agendar/', views.agendar_revision, name='agendar_revision'),
    path('editar/<int:pk>/', views.editar_seguimiento, name='editar_seguimiento'),
    path('detalle/<int:pk>/', views.detalle_seguimiento, name='detalle_seguimiento'),
    path('registrar/', views.registrar_seguimiento, name='registrar_seguimiento'),
    path('listar/', views.listar_seguimientos, name='listar_seguimientos'),
    path('veterinarios/', views.lista_veterinarios_refugio, name='lista_veterinarios_refugio'),
    path('veterinarios/agregar/', views.agregar_veterinario_refugio, name='agregar_veterinario_refugio'),
    path('veterinarios/editar/<int:pk>/', views.editar_veterinario_refugio, name='editar_veterinario_refugio'),
    path('veterinarios/eliminar/<int:pk>/', views.eliminar_veterinario_refugio, name='eliminar_veterinario_refugio'),
    path('veterinarios/', views.lista_veterinarios_refugio, name='lista_veterinarios_refugio'),
]