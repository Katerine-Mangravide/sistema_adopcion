from django.contrib import admin
from .models import Adoptante

@admin.register(Adoptante)
class AdoptanteAdmin(admin.ModelAdmin):
    list_display = ('user', 'cedula', 'telefono', 'direccion', 'fecha_registro')
    search_fields = ('user__first_name', 'user__last_name', 'cedula')
        