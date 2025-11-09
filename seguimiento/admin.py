from django.contrib import admin
from .models import Veterinario, Seguimiento
from usuarios.models import Veterinario


@admin.register(Veterinario)
class VeterinarioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido','telefono', 'refugio', 'email')
    search_fields = ('nombre', 'apellido', 'email')
    list_filter = ['refugio']


@admin.register(Seguimiento)
class SeguimientoAdmin(admin.ModelAdmin):
    list_display = ('id', 'mascota', 'veterinario', 'fecha_revision', 'hora_revision', 'estado')
    list_filter = ('estado', 'veterinario', 'fecha_revision')
    search_fields = ('mascota__nombre', 'veterinario__nombre', 'motivo')
