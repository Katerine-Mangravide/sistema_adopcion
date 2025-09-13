from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Adoptante

@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class UsuariosTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='juan', email='juan@mail.com', password='Pass1234')
        Adoptante.objects.create(user=self.user, cedula='1234567')

    def test_login_correcto(self):
        resp = self.client.post(reverse('usuarios:login'), {'username': 'juan', 'password': 'Pass1234'})
        self.assertEqual(resp.status_code, 302)
        self.assertTrue('_auth_user_id' in self.client.session)

    def test_login_incorrecto(self):
        resp = self.client.post(reverse('usuarios:login'), {'username': 'juan', 'password': 'wrong'})
        self.assertEqual(resp.status_code, 200)
        self.assertFalse('_auth_user_id' in self.client.session)

    def test_editar_perfil(self):
        self.client.login(username='juan', password='Pass1234')
        resp = self.client.post(reverse('usuarios:editar_perfil'), {'telefono':'0999123456', 'direccion':'Asunción'})
        adopt = Adoptante.objects.get(user=self.user)
        self.assertEqual(adopt.telefono, '0999123456')

    def test_desactivar(self):
        self.client.login(username='juan', password='Pass1234')
        resp = self.client.post(reverse('usuarios:desactivar_cuenta'))
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)

    def test_password_reset(self):
        resp = self.client.post(reverse('usuarios:password_reset'), {'email': 'juan@mail.com'})
        # locmem backend guarda mensajes en mail.outbox
        from django.core import mail
        self.assertEqual(len(mail.outbox), 1)
