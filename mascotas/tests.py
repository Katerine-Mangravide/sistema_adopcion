from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from unittest.mock import patch
from usuarios.models import Refugio, Adoptante
from .models import Mascota, SolicitudAdopcion

# ========================================================================
# CÓDIGO DE SETUP
# ========================================================================

class MascotaSetupMixin:
    """Mixin para crear rápidamente un usuario, refugio, mascota y adoptante."""
    def setUp(self):
        super().setUp()
        self.client = Client()

        # Usuario y refugio
        self.refugio_user = User.objects.create_user(
            username='refugio_test', 
            password='refugiopass', 
            email='refugio@test.com'
        )
        self.refugio = Refugio.objects.create(
            usuario=self.refugio_user,
            nombre='Refugio Central',
            direccion='Calle Refugio 101',
            telefono='021987654',
            email='refugio@test.com'
        )

        # Mascota (ArrayField como lista)
        self.mascota = Mascota.objects.create(
            nombre='Lulú',
            especie='Perro',
            raza='Beagle',
            edad=3,
            sexo='H',
            descripcion=['Muy juguetona.'],
            refugio=self.refugio
        )
        
        # Usuario adoptante
        self.adoptante_user = User.objects.create_user(
            username='adoptante_test',
            password='adoptantepass',
            first_name='Catherine',
            last_name='Test',
            email='catherine@adopt.com'
        )
        self.adoptante = Adoptante.objects.create(
            user=self.adoptante_user,
            cedula='999888777',
            telefono='0991123456',
            direccion='Av. Siempre Viva 742'
        )

# ========================================================================
# A. PRUEBAS DE MODELOS
# ========================================================================

class MascotaModelTests(MascotaSetupMixin, TestCase):

    def test_mascota_creation(self):
        self.assertTrue(Mascota.objects.filter(nombre='Lulú').exists())
        self.assertEqual(self.mascota.especie, 'Perro')
        self.assertFalse(self.mascota.adoptada)
        self.assertEqual(self.mascota.sexo, 'H')
        self.assertEqual(self.mascota.refugio.nombre, 'Refugio Central')
        self.assertEqual(self.mascota.descripcion, ['Muy juguetona.'])
        
    def test_solicitud_creation(self):
        solicitud = SolicitudAdopcion.objects.create(
            mascota=self.mascota,
            nombre_adoptante='Juan',
            apellido_adoptante='Perez',
            telefono='0982555666',
            email='juan.perez@test.com',
            direccion='Barrio Sol',
            estado='pendiente'
        )
        self.assertEqual(solicitud.mascota.nombre, 'Lulú')
        self.assertEqual(solicitud.estado, 'pendiente')
        self.assertEqual(solicitud.nombre_adoptante, 'Juan')
        
    def test_solicitud_aprobada_no_modifica_mascota(self):
        solicitud = SolicitudAdopcion.objects.create(
            mascota=self.mascota,
            nombre_adoptante='Test',
            apellido_adoptante='Test',
            telefono='000',
            email='test@test.com',
            direccion='Test',
            estado='aprobada'
        )
        self.mascota.refresh_from_db() 
        self.assertFalse(self.mascota.adoptada)

# ========================================================================
# B. PRUEBAS DE VISTAS (Solicitud de adopción)
# ========================================================================

class SolicitudAdopcionViewTests(MascotaSetupMixin, TestCase):

    @patch('mascotas.views.SolicitudAdopcionForm')
    def test_solicitar_adopcion_success(self, MockForm):
        self.client.login(username='adoptante_test', password='adoptantepass')

        mock_form_instance = MockForm.return_value
        mock_form_instance.is_valid.return_value = True
        mock_form_instance.cleaned_data = {
            'telefono': '0999111222',
            'direccion': 'Nueva Dirección',
            'nombre_adoptante': self.adoptante_user.first_name,
            'apellido_adoptante': self.adoptante_user.last_name,
            'email': self.adoptante_user.email
        }
        mock_form_instance.save.return_value = SolicitudAdopcion(
            mascota=self.mascota,
            nombre_adoptante='Catherine',
            apellido_adoptante='Test',
            email=self.adoptante_user.email,
            telefono='0999111222',
            direccion='Nueva Dirección'
        )

        response = self.client.post(
            reverse('mascotas:solicitar_adopcion', args=[self.mascota.id]),
            {
                'telefono': '0999111222',
                'direccion': 'Nueva Dirección'
            }
        )

        self.assertTrue(SolicitudAdopcion.objects.filter(mascota=self.mascota).exists())
        self.assertRedirects(response, reverse('usuarios:solicitud_enviada'))

    def test_solicitar_adopcion_duplicate_fail(self):
        self.client.login(username='adoptante_test', password='adoptantepass')

        SolicitudAdopcion.objects.create(
            mascota=self.mascota,
            nombre_adoptante='Test',
            apellido_adoptante='Test',
            telefono='000',
            email=self.adoptante_user.email,
            direccion='Test',
            estado='pendiente'
        )

        response = self.client.post(
            reverse('mascotas:solicitar_adopcion', args=[self.mascota.id]),
            {'telefono': '123', 'direccion': '456'}
        )

        self.assertRedirects(response, reverse('mascotas:detalle_mascota', args=[self.mascota.id]))
        self.assertEqual(SolicitudAdopcion.objects.filter(mascota=self.mascota).count(), 1)

# ========================================================================
# C. PRUEBAS DE GESTIÓN CRUD DE MASCOTAS
# ========================================================================

class MascotaManagementTests(MascotaSetupMixin, TestCase):

    def test_refugio_can_list_own_mascotas(self):
        self.client.login(username='refugio_test', password='refugiopass')
        otro_user = User.objects.create_user(username='otro', password='pass')
        otro_refugio = Refugio.objects.create(usuario=otro_user, nombre='Otro')
        Mascota.objects.create(nombre='Michi', especie='Gato', edad=1, refugio=otro_refugio)
        
        response = self.client.get(reverse('mascotas:lista_mascotas_refugio'))
        self.assertContains(response, 'Lulú')
        self.assertNotContains(response, 'Michi')
        
    def test_adoptante_cannot_access_management_pages(self):
        self.client.login(username='adoptante_test', password='adoptantepass')
        target_url = reverse('mascotas:lista_mascotas_refugio')
        expected_url = reverse('usuarios:login') + f'?next={target_url}'
        response = self.client.get(target_url)
        self.assertRedirects(response, expected_url)

    @patch('mascotas.views.MascotaForm')
    def test_refugio_can_edit_own_mascota(self, MockForm):
        self.client.login(username='refugio_test', password='refugiopass')
        mock_form_instance = MockForm.return_value
        mock_form_instance.is_valid.return_value = True

        response = self.client.post(
            reverse('mascotas:editar_mascota_refugio', args=[self.mascota.id]),
            {'nombre': 'Lulú Editada'},
            follow=True
        )

        self.assertContains(response, 'ha sido actualizada', html=False)

    def test_refugio_can_delete_own_mascota(self):
        self.client.login(username='refugio_test', password='refugiopass')
        response = self.client.post(
            reverse('mascotas:eliminar_mascota_refugio', args=[self.mascota.id]),
            follow=True
        )

        self.assertRedirects(response, reverse('mascotas:lista_mascotas_refugio'))
        self.assertContains(response, 'ha sido eliminada', html=False)
        self.assertFalse(Mascota.objects.filter(id=self.mascota.id).exists())
