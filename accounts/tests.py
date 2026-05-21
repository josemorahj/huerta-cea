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


class RegistroTest(TestCase):
    """Tests para register_view — HU-U1: Registro de usuario con rol voluntario."""

    def test_registro_exitoso(self):
        """POST con datos válidos crea usuario y redirige a home (/)."""
        response = self.client.post('/accounts/registro/', {
            'nombre': 'Maria',
            'apellido': 'Gomez',
            'email': 'maria@example.com',
            'username': 'maria',
            'password': 'segura123',
            'password2': 'segura123',
            'telefono': '987654321',
        })
        # register_view redirige a 'home' (que es /)
        self.assertRedirects(response, '/', fetch_redirect_response=False)

        usuario = User.objects.get(username='maria')
        self.assertEqual(usuario.email, 'maria@example.com')
        self.assertEqual(usuario.first_name, 'Maria')
        self.assertEqual(usuario.last_name, 'Gomez')
        self.assertEqual(usuario.rol, 'voluntario')
        self.assertEqual(usuario.telefono, '987654321')

    def test_registro_campos_vacios(self):
        """POST con campos obligatorios vacíos muestra error."""
        response = self.client.post('/accounts/registro/', {
            'nombre': '',
            'apellido': '',
            'email': '',
            'username': '',
            'password': '',
            'password2': '',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/register.html')
        self.assertContains(response, 'Todos los campos obligatorios deben estar completos.')

    def test_registro_contrasenas_no_coinciden(self):
        """POST con passwords distintas muestra error."""
        response = self.client.post('/accounts/registro/', {
            'nombre': 'Luis',
            'apellido': 'Perez',
            'email': 'luis@example.com',
            'username': 'luis',
            'password': 'secreta12',
            'password2': 'distinta12',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/register.html')
        self.assertContains(response, 'Las contrasenas no coinciden.')

    def test_registro_contrasena_corta(self):
        """POST con password < 6 caracteres muestra error."""
        response = self.client.post('/accounts/registro/', {
            'nombre': 'Ana',
            'apellido': 'Rivas',
            'email': 'ana@example.com',
            'username': 'ana',
            'password': 'ab12',
            'password2': 'ab12',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'La contrasena debe tener al menos 6 caracteres.')

    def test_registro_email_duplicado(self):
        """POST con email ya registrado muestra error."""
        User.objects.create_user(
            username='existente',
            email='yaexiste@example.com',
            password='pass123',
        )
        response = self.client.post('/accounts/registro/', {
            'nombre': 'Nuevo',
            'apellido': 'Usuario',
            'email': 'yaexiste@example.com',
            'username': 'nuevo',
            'password': 'segura123',
            'password2': 'segura123',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Este correo electronico ya esta registrado.')

    def test_registro_username_duplicado(self):
        """POST con username ya registrado muestra error."""
        User.objects.create_user(
            username='ocupado',
            email='otro@example.com',
            password='pass123',
        )
        response = self.client.post('/accounts/registro/', {
            'nombre': 'Nuevo',
            'apellido': 'Usuario',
            'email': 'nuevo@example.com',
            'username': 'ocupado',
            'password': 'segura123',
            'password2': 'segura123',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Este nombre de usuario ya esta en uso.')

    def test_registro_get_muestra_formulario(self):
        """GET a registro muestra el template."""
        response = self.client.get('/accounts/registro/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/register.html')

    def test_registro_usuario_autenticado_redirige(self):
        """Usuario ya logueado visitando registro es redirigido a home."""
        User.objects.create_user(
            username='logueado',
            password='pass123',
            rol='voluntario',
        )
        self.client.login(username='logueado', password='pass123')
        response = self.client.get('/accounts/registro/')
        self.assertRedirects(response, '/', fetch_redirect_response=False)


class LoginTest(TestCase):
    """Tests para login_view — HU-U2: Inicio de sesión."""

    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@cea.cl',
            password='admin123',
            first_name='Admin',
            rol='admin',
        )
        self.voluntario = User.objects.create_user(
            username='jvoluntario',
            email='voluntario@cea.cl',
            password='vol12345',
            first_name='Juan',
            rol='voluntario',
        )

    def test_login_admin_exitoso(self):
        """Admin logueado es redirigido a home (/)."""
        response = self.client.post('/accounts/iniciar-sesion/', {
            'username': 'admin',
            'password': 'admin123',
        })
        self.assertRedirects(response, '/', fetch_redirect_response=False)

    def test_login_voluntario_exitoso(self):
        """Voluntario logueado es redirigido a home (/)."""
        response = self.client.post('/accounts/iniciar-sesion/', {
            'username': 'jvoluntario',
            'password': 'vol12345',
        })
        self.assertRedirects(response, '/', fetch_redirect_response=False)

    def test_login_credenciales_incorrectas(self):
        """POST con credenciales inválidas muestra error y no redirige."""
        response = self.client.post('/accounts/iniciar-sesion/', {
            'username': 'admin',
            'password': 'wrongpass',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')
        self.assertContains(response, 'Credenciales incorrectas')

    def test_login_usuario_inexistente(self):
        """POST con username que no existe muestra error."""
        response = self.client.post('/accounts/iniciar-sesion/', {
            'username': 'nadie',
            'password': 'pass123',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Credenciales incorrectas')

    def test_login_get_muestra_formulario(self):
        """GET a login muestra el template."""
        response = self.client.get('/accounts/iniciar-sesion/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')

    def test_login_usuario_autenticado_redirige(self):
        """Usuario ya logueado visitando login es redirigido a home."""
        self.client.login(username='admin', password='admin123')
        response = self.client.get('/accounts/iniciar-sesion/')
        self.assertRedirects(response, '/', fetch_redirect_response=False)


class LogoutTest(TestCase):
    """Tests para logout_view."""

    def test_logout_redirige_a_login(self):
        """POST a logout cierra sesión y redirige a login."""
        User.objects.create_user(
            username='testuser',
            password='pass123',
            rol='voluntario',
        )
        self.client.login(username='testuser', password='pass123')
        response = self.client.post('/accounts/cerrar-sesion/')
        self.assertRedirects(response, '/accounts/iniciar-sesion/', fetch_redirect_response=False)

    def test_logout_requiere_post(self):
        """GET a logout debe devolver 405 (solo POST permitido)."""
        response = self.client.get('/accounts/cerrar-sesion/')
        self.assertEqual(response.status_code, 405)


class HomeViewTest(TestCase):
    """Tests para home_view — redirección según rol."""

    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin',
            password='admin123',
            rol='admin',
        )
        self.voluntario = User.objects.create_user(
            username='voluntario',
            password='pass123',
            rol='voluntario',
        )

    def test_home_admin_redirige_dashboard(self):
        """Admin autenticado en / es redirigido a dashboard."""
        self.client.login(username='admin', password='admin123')
        response = self.client.get('/')
        self.assertRedirects(response, '/dashboard/', fetch_redirect_response=False)

    def test_home_voluntario_redirige_activities(self):
        """Voluntario autenticado en / es redirigido a activities."""
        self.client.login(username='voluntario', password='pass123')
        response = self.client.get('/')
        self.assertRedirects(response, '/activities/', fetch_redirect_response=False)

    def test_home_sin_autenticar_redirige_login(self):
        """Usuario no autenticado en / es redirigido a login."""
        response = self.client.get('/')
        self.assertRedirects(response, '/accounts/iniciar-sesion/', fetch_redirect_response=False)
