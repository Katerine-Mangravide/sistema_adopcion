from django.db import models
from usuarios.models import Refugio, Veterinario
from mascotas.models import Mascota  # ajustar si el modelo Mascotas tiene otro nombre

class Seguimiento(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('en_curso', 'En curso'),
        ('finalizado', 'Finalizado'),
        ('cancelado', 'Cancelado'),
    ]

    mascota = models.ForeignKey(Mascota, on_delete=models.CASCADE)
    veterinario = models.ForeignKey(Veterinario, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_revision = models.DateField()
    hora_revision = models.TimeField(blank=True, null=True)
    motivo = models.CharField(max_length=200, blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Seguimiento #{self.id} - {self.mascota.nombre} - {self.fecha_revision}"
    