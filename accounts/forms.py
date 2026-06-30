from django import forms
from .models import User


class UsuarioForm(forms.ModelForm):
    """Edición de usuario existente por parte del admin (RF-10)."""

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'telefono', 'rol', 'is_active']
        labels = {
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'email': 'Correo electrónico',
            'telefono': 'Teléfono',
            'rol': 'Rol',
            'is_active': 'Activo',
        }


class UsuarioCrearForm(forms.ModelForm):
    """Alta de usuario por parte del admin (RF-10), con rol elegible y password."""

    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput,
        min_length=6,
    )
    password2 = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput,
        min_length=6,
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'telefono', 'rol']
        labels = {
            'username': 'Nombre de usuario',
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'email': 'Correo electrónico',
            'telefono': 'Teléfono',
            'rol': 'Rol',
        }

    def clean(self):
        cleaned = super().clean()
        password = cleaned.get('password')
        password2 = cleaned.get('password2')
        if password and password2 and password != password2:
            self.add_error('password2', 'Las contraseñas no coinciden.')
        return cleaned

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Este correo electrónico ya está registrado.')
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Este nombre de usuario ya está en uso.')
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user
