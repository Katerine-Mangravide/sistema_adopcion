from django.contrib.auth.models import User
from django.db import models

# Modelo Adoptante
class Adoptante(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # relación con el usuario Django
    cedula = models.CharField(max_length=20, unique=True)
    telefono = models.CharField(max_length=20, blank=True)
    direccion = models.CharField(max_length=200, blank=True)
    fecha_registro = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} ({self.cedula})"
    