from django import forms
from django.contrib.auth.models import User
from usuarios.models import Adoptante
from mascotas.models import Refugio, Mascota, SolicitudAdopcion

class CrearUsuarioForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Adoptante
        fields = ['cedula', 'telefono', 'direccion', 'avatar', 'foto_perfil']

class EditarUsuarioForm(forms.ModelForm):
    class Meta:
        model = Adoptante
        fields = ['cedula', 'telefono', 'direccion', 'avatar', 'foto_perfil']

class EditarUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

# ---- Refugio ----
class RefugioForm(forms.ModelForm):
    class Meta:
        model = Refugio
        fields = ['nombre', 'direccion', 'telefono', 'email']

# ---- Mascota ----
class MascotaForm(forms.ModelForm):
    class Meta:
        model = Mascota
        fields = ['nombre', 'especie', 'raza', 'edad', 'adoptada', 'imagen', 'refugio']

# ---- Solicitud ----
class SolicitudForm(forms.ModelForm):
    class Meta:
        model = SolicitudAdopcion
        fields = ['mascota', 'nombre_adoptante', 'apellido_adoptante', 'telefono', 'email', 'direccion', 'estado']

# ---- Solicitud (Específico para la Edición de Admin) ----
class SolicitudAdminForm(forms.ModelForm):
    class Meta:
        model = SolicitudAdopcion
        # Solo necesitamos los campos que el administrador va a cambiar
        fields = ['direccion', 'estado'] 
