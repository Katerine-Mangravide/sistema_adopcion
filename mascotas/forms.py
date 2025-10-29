from django import forms 
from .models import SolicitudAdopcion, Mascota 

class SolicitudAdopcionForm(forms.ModelForm):
    class Meta:
        model = SolicitudAdopcion
        fields = ['telefono', 'direccion']
        widgets = {
            'direccion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dirección completa'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número de teléfono'}),
        }

class EstadoSolicitudForm(forms.ModelForm):
    """Formulario simple para que el Refugio cambie el estado de la solicitud."""
    class Meta:
        model = SolicitudAdopcion
        fields = ['estado']

class MascotaForm(forms.ModelForm):
    """Formulario para añadir o editar una Mascota."""
    class Meta:
        model = Mascota
        # 🔑 CORRECCIÓN: INCLUYE 'refugio' para que el administrador lo seleccione
        fields = ['nombre', 'especie', 'raza', 'edad', 'sexo', 'descripcion', 'imagen', 'refugio'] 
        # Si no necesitas el campo 'adoptada' en el formulario, déjalo excluido.
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 4}),
            
        }