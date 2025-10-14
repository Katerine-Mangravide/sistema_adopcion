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
        # Excluye 'refugio' ya que se asigna automáticamente en la vista.
        # Excluye 'adoptada' ya que se actualiza automáticamente al aprobar.
        fields = ['nombre', 'especie', 'raza', 'edad', 'sexo', 'descripcion', 'imagen'] 
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 4}),
        }