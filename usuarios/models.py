from django.db import models
from django.contrib.auth.models import User

class Adoptante(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cedula = models.CharField(max_length=20, unique=True)
    telefono = models.CharField(max_length=20, blank=True)
    direccion = models.CharField(max_length=255, blank=True)
    # foto subida por el usuario (opcional)
    foto_perfil = models.ImageField(upload_to='profiles/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} ({self.cedula})"

class Refugio(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True) 
    
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=255)
    telefono = models.CharField(max_length=20)
    email = models.EmailField(unique=True) 
    
    # Campo que identifica el tipo de usuario (¡CLAVE!)
    es_refugio = models.BooleanField(default=True) 

    def __str__(self):
        return self.nombre      
    
class Veterinario(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100, default='Sin apellido')
    telefono = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    refugio = models.ForeignKey(Refugio, on_delete=models.CASCADE, related_name='veterinarios')

    def __str__(self):
        return self.nombre
    
    