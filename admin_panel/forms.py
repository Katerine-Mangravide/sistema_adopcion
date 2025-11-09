from django import forms
from django.contrib.auth.models import User
from usuarios.models import Adoptante
from mascotas.models import Refugio, Mascota, SolicitudAdopcion

class CrearRefugioUserForm(forms.Form):
    # Campos del User
    username = forms.CharField(max_length=150)
    email = forms.EmailField(required=False)
    first_name = forms.CharField(max_length=150, required=False)
    last_name = forms.CharField(max_length=150, required=False)
    
    # Campos de Contraseña
    password = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput, label='Confirmar Contraseña')

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password2 = cleaned_data.get("password2")

        if password and password != password2:
            self.add_error('password2', "Las contraseñas no coinciden.")
        
        # Validación de unicidad de username
        username = cleaned_data.get("username")
        if username and User.objects.filter(username=username).exists():
            self.add_error('username', "Este nombre de usuario ya está en uso.")
            
        return cleaned_data
        
    # 🔑 FIX CLAVE: Añadir el método save()
    def save(self, commit=True):
        """Crea el objeto User, hashea la contraseña y lo marca como staff."""
        # Usamos create_user para hashear la contraseña correctamente
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data.get('email', ''),
            password=self.cleaned_data['password'],
            first_name=self.cleaned_data.get('first_name', ''),
            last_name=self.cleaned_data.get('last_name', '')
        )
        
        # IMPORTANTE: Marcar como staff para que pueda acceder al admin_panel
        user.is_staff = True
        
        if commit:
            user.save()
            
        return user
    
class CrearUsuarioForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput, label='Confirmar contraseña')

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Las contraseñas no coinciden.')
        return cd['password2']

class EditarUsuarioForm(forms.ModelForm):
    class Meta:
        model = Adoptante
        fields = ['cedula', 'telefono', 'direccion', 'foto_perfil']

class EditarUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

# ---- Refugio ----
class RefugioForm(forms.ModelForm):
    class Meta:
        model = Refugio
        fields = ['nombre', 'direccion', 'telefono', 'email']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Esto hace que el formulario de Django no requiera el campo 'email'
        self.fields['email'].required = False

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