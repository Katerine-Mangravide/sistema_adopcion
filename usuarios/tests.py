from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from unittest.mock import patch
# Importa tus modelos
from .models import Adoptante, Refugio
# Importa tus formularios (necesario para el patch)
# **NOTA:** Si tus formularios se llaman diferente a RegistroForm, ajústalos aquí
# from .forms import RegistroForm, RegistroRefugioForm 


# ========================================================================
# A. PRUEBAS PARA LOS MODELOS EXTENDIDOS (Adoptante y Refugio)
# ========================================================================

class PerfilModelTests(TestCase):
    """
    Verifica que los modelos Adoptante y Refugio se creen correctamente
    y mantengan la relación OneToOne con el User de Django.
    """

    def test_create_adoptante_profile(self):
        """Asegura la creación correcta de un perfil Adoptante."""
        
        # 1. Crear el User base
        user = User.objects.create_user(
            username='catherine_test',
            password='Password123!',
            email='catherine@test.com'
        )

        # 2. Crear el perfil Adoptante asociado
        adoptante = Adoptante.objects.create(
            user=user,
            cedula='1234567',
            telefono='0981123456',
            direccion='Calle Falsa 123'
        )

        # Verificaciones
        self.assertEqual(adoptante.user.username, 'catherine_test')
        self.assertEqual(adoptante.cedula, '1234567')
        self.assertTrue(adoptante.is_active)
        self.assertIsInstance(user.adoptante, Adoptante)

    def test_create_refugio_profile(self):
        """Asegura la creación correcta de un perfil Refugio."""
        
        # 1. Crear el User base
        user = User.objects.create_user(
            username='refugio_py',
            password='refugioSeguro',
            email='refugio@test.com'
        )

        # 2. Crear el perfil Refugio asociado
        refugio = Refugio.objects.create(
            usuario=user,
            nombre='Refugio de Pruebas',
            direccion='Av. Central',
            telefono='021111222',
            email='refugio@test.com'
        )

        # Verificaciones
        self.assertEqual(refugio.nombre, 'Refugio de Pruebas')
        self.assertTrue(refugio.es_refugio)
        self.assertIsInstance(user.refugio, Refugio)


# ========================================================================
# B. PRUEBAS PARA LAS VISTAS DE AUTENTICACIÓN Y REGISTRO
# ========================================================================

# Nota: app_name='usuarios'. Usamos 'login', 'register', 'home', etc.

class AuthenticationViewTests(TestCase):
    """
    Verifica el flujo de registro y login. 
    """
    def setUp(self):
        self.client = Client()
        # Crear un usuario de prueba para login y testing de vistas protegidas
        self.user = User.objects.create_user(
            username='testuser', 
            email='test@example.com', 
            password='testpassword'
        )
        Adoptante.objects.create(user=self.user, cedula='1111111') # Crear perfil asociado

    # -- PRUEBA DE REGISTRO DE ADOPTANTE --
    # Usaremos patch para simular que RegistroForm es válido y pasa los datos
    # **IMPORTANTE:** El path debe coincidir con el nombre del módulo donde está RegistroForm
    @patch('usuarios.views.RegistroForm') 
    def test_register_adoptante_success(self, MockRegistroForm):
        """Asegura que la vista de registro de Adoptante crea el User y el perfil."""
        
        # Simular datos válidos del formulario
        mock_form_instance = MockRegistroForm.return_value
        mock_form_instance.is_valid.return_value = True
        mock_form_instance.cleaned_data = {
            'username': 'nuevo_adoptante',
            'password': 'passwordseguro',
            'first_name': 'Nuevo',
            'last_name': 'Adoptante',
            'email': 'nuevo@adopta.com',
            'cedula': '2222222',
        }
        
        # Simular que form.save() devuelve un Adoptante antes de guardarse
        mock_adoptante = Adoptante(cedula='2222222')
        mock_form_instance.save.return_value = mock_adoptante

        # Ejecutar la vista: CORREGIDO el nombre de la URL a 'register'
        response = self.client.post(reverse('usuarios:register'), {})

        # 1. Verificar creación en la base de datos
        self.assertTrue(User.objects.filter(username='nuevo_adoptante').exists())
        self.assertTrue(Adoptante.objects.filter(cedula='2222222').exists())
        
        # 2. Verificar redirección al Home después del registro y login
        self.assertRedirects(response, reverse('usuarios:perfil'))

    # -- PRUEBA DE REGISTRO DE REFUGIO --
    # **IMPORTANTE:** El path debe coincidir con el nombre del módulo donde está RegistroRefugioForm
    @patch('usuarios.views.RegistroRefugioForm')
    def test_register_refugio_success(self, MockRegistroRefugioForm):
        """Asegura que el registro de Refugio cree el User y el perfil Refugio."""
        
        # Simular datos válidos
        mock_form_instance = MockRegistroRefugioForm.return_value
        mock_form_instance.is_valid.return_value = True
        mock_form_instance.cleaned_data = {
            'username': 'refugio_test',
            'password': 'passwordrefugio',
            'first_name': 'Refugio',
            'last_name': 'Prueba',
            'email': 'refugio_nuevo@test.com',
            'nombre': 'Refugio Test OK', # Campo del modelo Refugio
        }

        # Simular el objeto Refugio guardado 
        mock_refugio = Refugio(nombre='Refugio Test OK')
        mock_form_instance.save.return_value = mock_refugio

        # Ejecutar la vista: CORREGIDO el nombre de la URL a 'register_refugio'
        response = self.client.post(reverse('usuarios:register_refugio'), {})

        # 1. Verificar creación en la base de datos
        self.assertTrue(User.objects.filter(username='refugio_test').exists())
        self.assertTrue(Refugio.objects.filter(nombre='Refugio Test OK').exists())
        
        # 2. Verificar redirección al panel del refugio
        self.assertRedirects(response, reverse('usuarios:panel_refugio'))
        
    # -- PRUEBA DE LOGIN DE ADOPTANTE/USUARIO --
    def test_login_success_redirect_home(self):
        """Asegura que un login exitoso redirige correctamente al home (si no es admin)."""
        
        # Simular datos de login válidos
        # CORREGIDO el nombre de la URL a 'login'
        response = self.client.post(reverse('usuarios:login'), {
            'username': 'testuser',
            'password': 'testpassword'
        }, follow=True) 

        # Verificar que el usuario esté logueado
        self.assertTrue('_auth_user_id' in self.client.session)
        
        # Verificar redirección
        self.assertRedirects(response, reverse('usuarios:perfil'))
        
    def test_login_admin_success_redirect_dashboard(self):
        """Asegura que un admin logueado redirige al admin_panel:dashboard."""
        
        # Crear un usuario admin de prueba
        admin_user = User.objects.create_superuser(
            username='admin_test', 
            email='admin@test.com', 
            password='adminpassword'
        )
        
        # Simular login del admin
        # CORREGIDO el nombre de la URL a 'login'
        response = self.client.post(reverse('usuarios:login'), {
            'username': 'admin_test',
            'password': 'adminpassword'
        }, follow=True) 
        
        # Verificar redirección al dashboard (asumiendo que 'admin_panel:dashboard' existe)
        self.assertRedirects(response, reverse('admin_panel:dashboard'))