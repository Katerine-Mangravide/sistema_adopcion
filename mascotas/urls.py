# mascotas/urls.py
from django.urls import path
from . import views

app_name = 'mascotas'

urlpatterns = [
    path('<int:mascota_id>/solicitar/', views.solicitar_adopcion, name='solicitar_adopcion'),
    path('<int:mascota_id>/', views.detalle_mascota, name='detalle_mascota'), 
    path('gestion/mis-mascotas/', views.lista_mascotas_refugio, name='lista_mascotas_refugio'),
    path('gestion/agregar-mascota/', views.agregar_mascota_refugio, name='agregar_mascota_refugio'),
    path('gestion/editar-mascota/<int:pk>/', views.editar_mascota, name='editar_mascota_refugio'),
    path('gestion/eliminar-mascota/<int:pk>/', views.eliminar_mascota, name='eliminar_mascota_refugio'),
    path('gestion/solicitudes/', views.gestion_solicitudes_refugio, name='gestion_solicitudes_refugio'),
    path('gestion/solicitud/<int:pk>/', views.detalle_solicitud_refugio, name='detalle_solicitud_refugio'),

]
