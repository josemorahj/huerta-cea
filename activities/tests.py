from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from datetime import date, time
from .models import Actividad, Inscripcion

User = get_user_model()


class InscripcionDuplicadaTest(TestCase):
    """HU-I1: Verifica que un voluntario no pueda inscribirse dos veces a la misma actividad."""

    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin',
            password='pass123',
            rol='admin',
        )
        self.voluntario = User.objects.create_user(
            username='voluntario',
            password='pass123',
            rol='voluntario',
        )
        self.actividad = Actividad.objects.create(
            titulo='Taller de Compostaje',
            descripcion='Aprende a hacer compost',
            fecha=date(2026, 6, 15),
            hora=time(10, 0),
            lugar='Huerta CEA',
            cupo_maximo=10,
            responsable=self.admin,
        )

    def test_inscripcion_duplicada_rechazada(self):
        """Un voluntario no puede inscribirse dos veces a la misma actividad."""
        Inscripcion.objects.create(
            actividad=self.actividad,
            voluntario=self.voluntario,
            estado='CONFIRMADA',
        )

        inscripcion_duplicada = Inscripcion(
            actividad=self.actividad,
            voluntario=self.voluntario,
            estado='CONFIRMADA',
        )

        with self.assertRaises(ValidationError):
            inscripcion_duplicada.full_clean()
            inscripcion_duplicada.save()


class CupoMaximoTest(TestCase):
    """RF-05: Verifica que no se pueda inscribir más voluntarios que el cupo máximo."""

    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin',
            password='pass123',
            rol='admin',
        )
        self.actividad = Actividad.objects.create(
            titulo='Taller de Riego',
            descripcion='Técnicas de riego eficiente',
            fecha=date(2026, 7, 1),
            hora=time(9, 0),
            lugar='Huerta CEA',
            cupo_maximo=1,
            responsable=self.admin,
        )

    def test_cupo_lleno_rechaza_nueva_inscripcion(self):
        """Cuando el cupo está lleno, una nueva inscripción debe ser rechazada."""
        voluntario1 = User.objects.create_user(
            username='voluntario1',
            password='pass123',
            rol='voluntario',
        )
        voluntario2 = User.objects.create_user(
            username='voluntario2',
            password='pass123',
            rol='voluntario',
        )

        Inscripcion.objects.create(
            actividad=self.actividad,
            voluntario=voluntario1,
            estado='CONFIRMADA',
        )

        inscripcion_excedida = Inscripcion(
            actividad=self.actividad,
            voluntario=voluntario2,
            estado='CONFIRMADA',
        )

        with self.assertRaises(ValidationError):
            inscripcion_excedida.full_clean()
            inscripcion_excedida.save()

