from django import forms
from django.contrib.auth.models import User
from .models import Adoptante, Refugio

class RegistroForm(forms.ModelForm):
    # campos extra para crear el User
    username = forms.CharField(max_length=150, label="Usuario")
    password = forms.CharField(widget=forms.PasswordInput, label="Contraseña")
    password2 = forms.CharField(widget=forms.PasswordInput, label="Confirmar contraseña")
    first_name = forms.CharField(max_length=30, required=False, label="Nombre")
    last_name = forms.CharField(max_length=150, required=False, label="Apellido")
    email = forms.EmailField(required=False, label="Email")

    class Meta:
        model = Adoptante
        fields = ['cedula', 'telefono', 'direccion']  # no avatar ni foto aquí (avatar sólo en editar)

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("El nombre de usuario ya está en uso.")
        return username

    def clean(self):
        cleaned = super().clean()
        pw = cleaned.get('password')
        pw2 = cleaned.get('password2')
        if pw and pw2 and pw != pw2:
            self.add_error('password2', 'Las contraseñas no coinciden.')
        return cleaned

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

class AdoptanteForm(forms.ModelForm):
    class Meta:
        model = Adoptante
        fields = ['cedula', 'telefono', 'direccion', 'avatar', 'foto_perfil']
        widgets = {
            'avatar': forms.RadioSelect(),  # renderiza radios (pero en template los mostraremos con imágenes)
        }

class RegistroRefugioForm(forms.ModelForm):
    # Campos para crear el User, idénticos al RegistroForm de Adoptante
    username = forms.CharField(max_length=150, label="Usuario")
    password = forms.CharField(widget=forms.PasswordInput, label="Contraseña")
    password2 = forms.CharField(widget=forms.PasswordInput, label="Confirmar contraseña")
    first_name = forms.CharField(max_length=30, required=False, label="Nombre Contacto")
    last_name = forms.CharField(max_length=150, required=False, label="Apellido Contacto")
    email = forms.EmailField(required=True, label="Email (Acceso)") # Email requerido para Refugio

    class Meta:
        model = Refugio
        # Campos del modelo Refugio que se rellenan en el registro
        fields = ['nombre', 'direccion', 'telefono'] 

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("El nombre de usuario ya está en uso.")
        return username

    def clean(self):
        cleaned = super().clean()
        pw = cleaned.get('password')
        pw2 = cleaned.get('password2')
        if pw and pw2 and pw != pw2:
            self.add_error('password2', 'Las contraseñas no coinciden.')
        return cleaned

# Formulario para editar el perfil del Refugio
class RefugioForm(forms.ModelForm):
    class Meta:
        model = Refugio
        fields = ['nombre', 'direccion', 'telefono']        