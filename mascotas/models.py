from django.db import models
from usuarios.models import Refugio
from django.contrib.postgres.fields import ArrayField # <-- ¡IMPORTACIÓN CLAVE!


# Modelo Mascota
class Mascota(models.Model):
    # Opciones para Sexo
    SEXO_CHOICES = [
        ('M', 'Macho'),
        ('H', 'Hembra'),
    ]
    nombre = models.CharField(max_length=100)
    especie = models.CharField(max_length=50)
    raza = models.CharField(max_length=50, blank=True)
    edad = models.IntegerField()
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES, default='M')
    descripcion = ArrayField(
        models.CharField(max_length=500),
        default=list,                     
        blank=True,
    ) 
    fecha_ingreso = models.DateField(auto_now_add=True)
    adoptada = models.BooleanField(default=False)
    imagen = models.ImageField(upload_to='mascotas/', blank=True, null=True)
    refugio = models.ForeignKey(Refugio, on_delete=models.CASCADE, related_name='mascotas')
    
    def __str__(self):
        return f"{self.nombre} ({self.especie})"

# Modelo Solicitud adopcion
class SolicitudAdopcion(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('aprobada', 'Aprobada'),
        ('rechazada', 'Rechazada'),
    ]

    mascota = models.ForeignKey(Mascota, on_delete=models.CASCADE)
    nombre_adoptante = models.CharField(max_length=100)
    apellido_adoptante = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)
    email = models.EmailField()
    direccion = models.CharField(max_length=200)
    fecha_solicitud = models.DateField(auto_now_add=True)
    estado = models.CharField(max_length=10, choices=ESTADOS, default='pendiente')

    def __str__(self):
        return f"Solicitud de {self.nombre_adoptante} {self.apellido_adoptante} - {self.mascota.nombre}"
