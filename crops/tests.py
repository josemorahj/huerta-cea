from django.test import TestCase
from .models import Especie


class BuscadorFichasTest(TestCase):

    def setUp(self):
        Especie.objects.create(
            nombre_comun="Lechuga",
            nombre_cientifico="Lactuca sativa",
            descripcion="Lechuga crespa",
            condiciones_cultivo="Suelo suelto",
            frecuencia_riego="Cada 2 dias",
            temporada_recomendada="ANUAL",
        )

    def test_busqueda_parcial_insensible_a_mayusculas(self):
        resultado = Especie.objects.filter(nombre_comun__icontains="lech")
        self.assertEqual(resultado.count(), 1)

        resultado = Especie.objects.filter(nombre_comun__icontains="LECHUGA")
        self.assertEqual(resultado.count(), 1)

    def test_busqueda_sin_resultados(self):
        resultado = Especie.objects.filter(nombre_comun__icontains="tomate")
        self.assertEqual(resultado.count(), 0)