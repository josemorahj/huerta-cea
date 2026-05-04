from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class AccesoDashboardTest(TestCase):
    """Verifica que un voluntario no pueda acceder a /dashboard/ y sea redirigido."""

    def test_voluntario_redirigido_de_dashboard(self):
        """Un voluntario autenticado es redirigido a activities:list."""
        voluntario = User.objects.create_user(
            username='voluntario',
            password='pass123',
            rol='voluntario',
        )
        self.client.login(username='voluntario', password='pass123')

        response = self.client.get('/dashboard/', follow=False)

        self.assertRedirects(response, '/activities/', fetch_redirect_response=False)

