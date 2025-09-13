from django.contrib import admin
from .models import Mascota, Refugio, SolicitudAdopcion

# Registrar Mascota en el admin
@admin.register(Mascota)
class MascotaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'especie', 'raza', 'edad', 'adoptada', 'fecha_ingreso', 'refugio')
    list_filter = ('especie', 'adoptada', 'refugio')
    search_fields = ('nombre', 'raza', 'refugio__nombre')

# Registrar Refugio en el admin
@admin.register(Refugio)
class RefugioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'direccion', 'telefono', 'email')
    search_fields = ('nombre', 'direccion')

@admin.register(SolicitudAdopcion)
class SolicitudAdopcionAdmin(admin.ModelAdmin):
    list_display = ('nombre_adoptante', 'apellido_adoptante', 'mascota', 'estado', 'fecha_solicitud')
    list_filter = ('estado',)
    search_fields = ('nombre_adoptante', 'apellido_adoptante', 'mascota__nombre')
