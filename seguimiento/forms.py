from django import forms
from .models import Seguimiento
from usuarios.models import Veterinario


class SeguimientoForm(forms.ModelForm):
    class Meta:
        model = Seguimiento
        fields = ['mascota', 'veterinario', 'fecha_revision', 'hora_revision', 'motivo', 'observaciones', 'estado']
        widgets = {
            'fecha_revision': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'hora_revision': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'motivo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Motivo de la revisión'}),
            'observaciones': forms.Textarea(attrs={'rows': 4, 'class': 'form-control', 'placeholder': 'Escribe las observaciones'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        refugio = kwargs.pop('refugio', None)
        super().__init__(*args, **kwargs)
        if refugio:
            # Solo muestra los veterinarios del refugio logueado
            self.fields['veterinario'].queryset = Veterinario.objects.filter(refugio=refugio)
        else:
            # En caso de no haber refugio (seguridad)
            self.fields['veterinario'].queryset = Veterinario.objects.none()


class VeterinarioForm(forms.ModelForm):
    class Meta:
        model = Veterinario
        fields = ['nombre', 'telefono', 'apellido', 'email']  # No incluimos refugio, se asigna automáticamente
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellido'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número de teléfono'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo electrónico'}),
        }
