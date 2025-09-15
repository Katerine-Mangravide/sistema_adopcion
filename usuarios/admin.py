from django.contrib import admin
from .models import Adoptante

@admin.register(Adoptante)
class AdoptanteAdmin(admin.ModelAdmin):
    list_display = ('user', 'email', 'cedula', 'telefono', 'direccion', 'fecha_registro')
    search_fields = ('user__first_name', 'user__last_name', 'cedula', 'user__email')

    def email(self, obj):
        return obj.user.email
    email.admin_order_field = 'user__email'
    email.short_description = 'Email'
        