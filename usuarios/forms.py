from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Adoptante

class RegistroForm(forms.ModelForm):
    username = forms.CharField()
    first_name = forms.CharField(label="Nombre")
    last_name = forms.CharField(label="Apellido")
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Adoptante
        fields = ["cedula", "telefono", "direccion", "avatar"]

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password and confirm_password and password != confirm_password:
            self.add_error("confirm_password", "Las contraseñas no coinciden.")
        return cleaned_data

    def save(self, commit=True):
        # Crear el usuario
        user = User(
            username=self.cleaned_data["username"],
            first_name=self.cleaned_data["first_name"],   # 👈 ahora se guarda
            last_name=self.cleaned_data["last_name"],     # 👈 ahora también
            email=self.cleaned_data["email"]
        )
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()

        # Crear adoptante vinculado
        adoptante = super().save(commit=False)
        adoptante.user = user
        if commit:
            adoptante.save()
        return adoptante

class PerfilForm(forms.ModelForm):
    class Meta:
        model = Adoptante
        fields = ['telefono', 'direccion', 'avatar']

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

class AdoptanteForm(forms.ModelForm):
    class Meta:
        model = Adoptante
        fields = ['cedula', 'telefono', 'direccion', 'avatar']