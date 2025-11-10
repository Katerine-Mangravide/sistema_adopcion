from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from datetime import date, time

from usuarios.models import Refugio, Veterinario, Adoptante
from mascotas.models import Mascota
from seguimiento.models import Seguimiento


# ===========================================================
# A. TESTS DE MODELO
# ===========================================================
class SeguimientoModelTests(TestCase):
    """Verifica la creación y los campos del modelo Seguimiento."""

    def setUp(self):
        # Usuario y refugio
        self.user_refugio = User.objects.create_user(username='refugio_user', password='testpass')
        self.refugio = Refugio.objects.create(
            usuario=self.user_refugio,
            nombre='Refugio San Roque',
            direccion='Av. Central 123',
            telefono='021123456',
            email='sanroque@test.com',
            es_refugio=True
        )

        # Veterinario ligado al refugio
        self.vet = Veterinario.objects.create(
            nombre='Dr. López',
            apellido='Martínez',
            telefono='0991555555',
            email='vet@test.com',
            refugio=self.refugio
        )

        # Mascota ligada al refugio
        self.mascota = Mascota.objects.create(
            nombre='Firulais',
            especie='Perro',
            raza='Mestizo',
            edad=3,
            sexo='M',
            refugio=self.refugio
        )

    def test_create_seguimiento(self):
        """Asegura que se cree un seguimiento correctamente."""
        seg = Seguimiento.objects.create(
            mascota=self.mascota,
            veterinario=self.vet,
            fecha_revision=date.today(),
            hora_revision=time(10, 30),
            motivo='Control general',
            observaciones='El perro está sano.',
            estado='pendiente'
        )
        self.assertEqual(seg.mascota.nombre, 'Firulais')
        self.assertEqual(seg.mascota.refugio.nombre, 'Refugio San Roque')
        self.assertEqual(seg.veterinario.nombre, 'Dr. López')
        self.assertEqual(seg.estado, 'pendiente')
        self.assertIn('Firulais', str(seg))


# ===========================================================
# B. TESTS DE VISTAS
# ===========================================================
class SeguimientoViewsTests(TestCase):
    """Prueba las vistas principales del módulo seguimiento."""

    def setUp(self):
        self.client = Client()

        # ---------------------------
        # Usuario y refugio
        # ---------------------------
        self.user_refugio = User.objects.create_user(username='refugio_user', password='12345')
        self.refugio = Refugio.objects.create(
            usuario=self.user_refugio,
            nombre='Refugio Amigos Peludos',
            direccion='Ruta 1 Km 12',
            telefono='021999888',
            email='amigos@test.com',
            es_refugio=True
        )

        # Veterinario ligado al refugio
        self.vet = Veterinario.objects.create(
            nombre='María',
            apellido='Gómez',
            telefono='0991777777',
            email='maria@test.com',
            refugio=self.refugio
        )

        # ---------------------------
        # Usuario adoptante
        # ---------------------------
        self.user_adoptante = User.objects.create_user(username='adoptante_user', password='12345')
        self.adoptante = Adoptante.objects.create(
            user=self.user_adoptante,
            cedula='4567890'
        )

        # ---------------------------
        # Mascota ligada al refugio
        # ---------------------------
        self.mascota = Mascota.objects.create(
            nombre='Luna',
            especie='Gato',
            raza='Siamesa',
            edad=2,
            sexo='H',
            refugio=self.refugio
        )

        # Seguimiento ligado a mascota y veterinario
        self.seguimiento = Seguimiento.objects.create(
            mascota=self.mascota,
            veterinario=self.vet,
            fecha_revision=date.today(),
            hora_revision=time(9, 0),
            motivo='Chequeo inicial',
            estado='pendiente'
        )

    # ---------------------------
    # Vistas refugio
    # ---------------------------
    def test_lista_seguimientos_view_refugio(self):
        """Verifica que el refugio pueda acceder a la lista de seguimientos."""
        self.client.login(username='refugio_user', password='12345')
        response = self.client.get(reverse('seguimiento:listar_seguimientos'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'seguimiento/listar_seguimientos.html')
        self.assertContains(response, self.seguimiento.mascota.nombre)

    def test_agendar_revision_view_get(self):
        """Verifica GET del formulario de agendar revisión para refugio."""
        self.client.login(username='refugio_user', password='12345')
        response = self.client.get(reverse('seguimiento:agendar_revision'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'seguimiento/agendar_revision.html')

    def test_agendar_revision_view_post(self):
        """Verifica POST del formulario de agendar revisión para refugio."""
        self.client.login(username='refugio_user', password='12345')
        response = self.client.post(
            reverse('seguimiento:agendar_revision'),
            data={
                'mascota': self.mascota.id,
                'veterinario': self.vet.id,
                'fecha_revision': date.today().strftime('%Y-%m-%d'),
                'hora_revision': '10:00',
                'motivo': 'Chequeo',
                'observaciones': 'Todo ok',
                'estado': 'pendiente'
            }
        )
        self.assertEqual(response.status_code, 302)  # Redirige tras guardar
        self.assertTrue(Seguimiento.objects.filter(motivo='Chequeo').exists())

    def test_adoptante_no_puede_agendar_revision(self):
        """Verifica que un adoptante no pueda acceder al formulario de agendar revisión."""
        self.client.login(username='adoptante_user', password='12345')
        response = self.client.get(reverse('seguimiento:agendar_revision'))
        self.assertIn(response.status_code, [302, 403])  # Redirigido o prohibido

    # ---------------------------
    # Vistas adoptante
    # ---------------------------
def test_mis_seguimientos_view_adoptante(self):
    """Verifica que el adoptante pueda ver sus seguimientos."""
    # Asociamos la mascota al adoptante y la marcamos como adoptada
    self.mascota.adoptante = self.adoptante
    self.mascota.adoptada = True
    self.mascota.save()

    # Asociamos el seguimiento a la mascota adoptada
    self.seguimiento.mascota = self.mascota
    self.seguimiento.save()

    self.client.login(username='adoptante_user', password='12345')
    response = self.client.get(reverse('usuarios:mis_seguimientos'))
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, 'usuarios/mis_seguimientos.html')
    self.assertContains(response, self.mascota.nombre)
