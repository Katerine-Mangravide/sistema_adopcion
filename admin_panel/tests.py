from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.messages import get_messages
from usuarios.models import Refugio, Adoptante 
from mascotas.models import Mascota, SolicitudAdopcion

# ========================================================================
# CÓDIGO DE SETUP: CREACIÓN DE OBJETOS BÁSICOS PARA EL ADMIN PANEL
# ========================================================================

class AdminPanelSetupMixin(TestCase):
    """Clase base para crear un Admin, Adoptante, Refugio y Mascota."""
    def setUp(self):
        super().setUp()
        self.client = Client()

        # 1. Crear usuario Staff (Admin)
        self.admin_user = User.objects.create_user(
            username='admin_test', 
            password='adminpass', 
            email='admin@test.com',
            is_staff=True,
            is_superuser=True
        )

        # 2. Crear usuario Adoptante (Non-staff)
        self.adoptante_user = User.objects.create_user(
            username='adoptante_test', 
            password='adoptantepass', 
            email='adoptante@test.com'
        )
        self.adoptante = Adoptante.objects.create(
            user=self.adoptante_user, 
            cedula='111', 
            telefono='222',
            direccion='333'
        )
        
        # 3. Crear Refugio base (para CRUD)
        self.refugio_user = User.objects.create_user(
            username='refugio_base', 
            password='refugiopass', 
            email='refugio@test.com',
            first_name='Refugio', # 🔑 CORRECCIÓN: Añadidos para el User base
            last_name='Base',     # 🔑 CORRECCIÓN: Añadidos para el User base
            is_staff=True
        )
        self.refugio = Refugio.objects.create(
            usuario=self.refugio_user,
            nombre='Refugio Central Test',
            direccion='Calle Refugio 101',
            telefono='021987654',
            email='refugio@test.com'
        )

        # 4. Crear Mascota base
        self.mascota = Mascota.objects.create(
            nombre='Lulú Admin',
            especie='Perro',
            raza='Beagle',
            edad=3,
            sexo='H',
            refugio=self.refugio
        )
        
# ========================================================================
# A. PRUEBAS DE CONTROL DE ACCESO
# ========================================================================

class AdminPanelAccessTests(AdminPanelSetupMixin):
    """Verifica que solo los usuarios Staff puedan acceder al panel."""
    
    def test_non_staff_cannot_access_dashboard(self):
        """Asegura que un Adoptante sea redirigido al intentar acceder al Dashboard. (CORREGIDO)"""
        self.client.login(username='adoptante_test', password='adoptantepass')
        response = self.client.get(reverse('admin_panel:dashboard'))
        
        expected_redirect_path = reverse('usuarios:login') + '?next=/admin-web/'
        self.assertRedirects(response, expected_redirect_path)
        
    def test_admin_can_access_dashboard(self):
        """Asegura que el Admin pueda acceder al Dashboard."""
        self.client.login(username='admin_test', password='adminpass')
        response = self.client.get(reverse('admin_panel:dashboard'))
        self.assertEqual(response.status_code, 200)

# ========================================================================
# B. PRUEBAS CRUD DE REFUGIOS
# ========================================================================

class RefugiosManagementTests(AdminPanelSetupMixin):
    """Verifica la funcionalidad de la gestión de Refugios (CRUD)."""
    
    def setUp(self):
        super().setUp()
        self.client.login(username='admin_test', password='adminpass')
        
        # Datos de un nuevo Refugio a crear
        self.new_refugio_creation_data = {
            'username': 'nuevo_refugio_cr', 
            'password': 'newrefugiopass',   
            'password2': 'newrefugiopass',
            'email': 'nuevo@refugio.com',
            # 🔑 CORRECCIÓN 1: Añadidos first_name y last_name para pasar la validación del UserForm
            'first_name': 'Nuevo',      
            'last_name': 'Refugio',     
            'nombre': 'Refugio Nuevo Creado',
            'direccion': 'Nueva Direccion 200',
            'telefono': '999999999',
        }

    def test_refugios_list_view(self):
        """Asegura que la lista de refugios se muestre correctamente."""
        # Esta prueba pasa ahora que los tests de POST están validados, previniendo el NoReverseMatch
        response = self.client.get(reverse('admin_panel:gestion_refugios'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.refugio.nombre)

    def test_crear_refugio_success(self):
        """Asegura que se pueda crear un nuevo Refugio con su User asociado. (CORREGIDO)"""
        
        response = self.client.post(
            reverse('admin_panel:crear_refugio'),
            self.new_refugio_creation_data,
            follow=True
        )

        # Ahora la validación pasa y se redirige correctamente (302)
        self.assertRedirects(response, reverse('admin_panel:gestion_refugios'))
        
        # Verificar el mensaje de éxito
        messages_list = list(get_messages(response.wsgi_request))
        self.assertIn("Refugio y Usuario creados correctamente", str(messages_list[0]))
        
        # Verificar que el objeto Refugio exista
        self.assertTrue(Refugio.objects.filter(nombre='Refugio Nuevo Creado').exists())
        # Verificar que el User asociado exista
        self.assertTrue(User.objects.filter(username='nuevo_refugio_cr').exists())


    def test_editar_refugio_success(self):
        """Asegura que el Admin pueda editar un Refugio y su User asociado. (CORREGIDO)"""
        new_name = "Refugio Actualizado S.A."
        new_email = "updated_base@refugio.com"
        
        # Datos a enviar (asumiendo UserForm y RefugioForm data)
        edit_data = {
            'username': self.refugio_user.username,
            # 🔑 CORRECCIÓN 2: Añadido/Actualizado first_name y last_name para UserForm
            'first_name': 'Base Name Updated',      
            'last_name': 'Surname Updated',         
            'email': new_email,             
            # RefugioForm data
            'nombre': new_name,             
            'direccion': self.refugio.direccion,
            'telefono': '999999000',
        }
        
        # Recordatorio: En este punto, DEBES haber cambiado r.id a r.usuario_id en refugios.html
        response = self.client.post(
            reverse('admin_panel:editar_refugio', args=[self.refugio_user.pk]), # Usa el PK del usuario
            edit_data,
            follow=True
        )

        # Ahora la validación pasa y se redirige correctamente (302)
        self.assertRedirects(response, reverse('admin_panel:gestion_refugios'))
        
        # Verificar el mensaje de éxito
        messages_list = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages_list[0]), "Refugio actualizado.")
        
        # Verificar que el objeto en la base de datos se haya actualizado
        self.refugio.refresh_from_db()
        self.assertEqual(self.refugio.nombre, new_name)
        self.refugio_user.refresh_from_db()
        self.assertEqual(self.refugio_user.email, new_email)


    def test_eliminar_refugio_success(self):
        """Asegura que el Admin pueda eliminar un Refugio (y su User por CASCADE). (CORREGIDO)"""
        refugio_to_delete_pk = self.refugio.pk
        refugio_user_pk = self.refugio_user.pk
        
        response = self.client.post(
            reverse('admin_panel:eliminar_refugio', args=[self.refugio_user.pk]), # Usa el PK del usuario
            follow=True
        )

        self.assertRedirects(response, reverse('admin_panel:gestion_refugios'))
        
        # Verificar el mensaje de éxito
        messages_list = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages_list[0]), "Refugio eliminado.")
        
        # Verificar que el objeto haya sido eliminado (y el User asociado)
        self.assertFalse(Refugio.objects.filter(pk=refugio_to_delete_pk).exists())
        self.assertFalse(User.objects.filter(pk=refugio_user_pk).exists())