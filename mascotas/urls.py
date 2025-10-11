# mascotas/urls.py
from django.urls import path
from . import views

app_name = 'mascotas'

urlpatterns = [
    path('<int:mascota_id>/solicitar/', views.solicitar_adopcion, name='solicitar_adopcion'),
]
