from django.db import models
from django.contrib.auth.models import User

AVATAR_CHOICES = [
    ('avatar1.png', 'Avatar 1'),
    ('avatar2.png', 'Avatar 2'),
    ('avatar3.png', 'Avatar 3'),
    ('avatar4.png', 'Avatar 4'),
    ('avatar5.png', 'Avatar 5'),
]

class Adoptante(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cedula = models.CharField(max_length=20, unique=True)
    telefono = models.CharField(max_length=20, blank=True)
    direccion = models.CharField(max_length=255, blank=True)
    # foto subida por el usuario (opcional)
    foto_perfil = models.ImageField(upload_to='profiles/', blank=True, null=True)
    # avatar fijo (elige entre los assets estáticos)
    avatar = models.CharField(max_length=100, choices=AVATAR_CHOICES, blank=True)
    is_active = models.BooleanField(default=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} ({self.cedula})"

        