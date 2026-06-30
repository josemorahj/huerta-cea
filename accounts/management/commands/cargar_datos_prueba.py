import secrets
import string
from datetime import date, time, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


def generar_password():
    """Genera una contraseña aleatoria segura de 12 caracteres."""
    alfabeto = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alfabeto) for _ in range(12))
from crops.models import Especie, CicloCultivo
from activities.models import Actividad, Inscripcion

User = get_user_model()


class Command(BaseCommand):
    help = "Carga datos ficticios de prueba para huerta-cea (admins, voluntarios, especies, ciclos, actividades e inscripciones)."

    def handle(self, *args, **options):
        self.stdout.write("Creando usuarios...")

        credenciales = []

        admin1, _ = User.objects.get_or_create(
            username="admin_jose",
            defaults={
                "email": "admin.jose@cea.cl",
                "first_name": "Jose",
                "last_name": "Mora",
                "rol": "admin",
                "telefono": "+56911111111",
                "is_staff": True,
                "is_superuser": True,
            },
        )
        if not admin1.has_usable_password():
            pw = generar_password()
            admin1.set_password(pw)
            admin1.save()
            credenciales.append(("admin_jose", pw, "admin, superusuario"))

        admin2, _ = User.objects.get_or_create(
            username="admin_carla",
            defaults={
                "email": "carla.coordinadora@cea.cl",
                "first_name": "Carla",
                "last_name": "Reyes",
                "rol": "admin",
                "telefono": "+56922222222",
                "is_staff": True,
            },
        )
        if not admin2.has_usable_password():
            pw = generar_password()
            admin2.set_password(pw)
            admin2.save()
            credenciales.append(("admin_carla", pw, "admin"))

        voluntarios_data = [
            ("vol_pedro", "Pedro", "Soto", "pedro.soto@mail.com", "+56933333333"),
            ("vol_maria", "Maria", "Lopez", "maria.lopez@mail.com", "+56944444444"),
            ("vol_diego", "Diego", "Fuentes", "diego.fuentes@mail.com", "+56955555555"),
            ("vol_andrea", "Andrea", "Vega", "andrea.vega@mail.com", "+56966666666"),
            ("vol_tomas", "Tomas", "Rojas", "tomas.rojas@mail.com", "+56977777777"),
        ]

        voluntarios = []
        for username, first, last, email, tel in voluntarios_data:
            user, _ = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": email,
                    "first_name": first,
                    "last_name": last,
                    "rol": "voluntario",
                    "telefono": tel,
                },
            )
            if not user.has_usable_password():
                pw = generar_password()
                user.set_password(pw)
                user.save()
                credenciales.append((username, pw, "voluntario"))
            voluntarios.append(user)

        self.stdout.write("Creando especies...")

        especies_data = [
            ("Tomate", "Solanum lycopersicum", "PRIMAVERA_VERANO", "Cada 2 dias"),
            ("Lechuga", "Lactuca sativa", "OTONIO_INVIERNO", "Diario"),
            ("Zanahoria", "Daucus carota", "ANUAL", "3 veces por semana"),
            ("Acelga", "Beta vulgaris", "OTONIO_INVIERNO", "Cada 2 dias"),
            ("Frutilla", "Fragaria x ananassa", "PRIMAVERA_VERANO", "Diario"),
        ]

        especies = {}
        for nombre, cientifico, temporada, riego in especies_data:
            especie, _ = Especie.objects.get_or_create(
                nombre_comun=nombre,
                defaults={
                    "nombre_cientifico": cientifico,
                    "descripcion": f"Ficha de referencia para el cultivo de {nombre.lower()} en la huerta del CEA.",
                    "condiciones_cultivo": "Suelo bien drenado, exposicion solar directa, riego regular.",
                    "frecuencia_riego": riego,
                    "temporada_recomendada": temporada,
                },
            )
            especies[nombre] = especie

        self.stdout.write("Creando ciclos de cultivo...")

        hoy = date.today()
        ciclos_data = [
            ("Tomate", hoy - timedelta(days=40), hoy + timedelta(days=20), "EN_CRECIMIENTO"),
            ("Lechuga", hoy - timedelta(days=10), hoy + timedelta(days=20), "SEMBRADO"),
            ("Zanahoria", hoy - timedelta(days=60), hoy - timedelta(days=5), "LISTO_COSECHA"),
            ("Acelga", hoy - timedelta(days=90), hoy - timedelta(days=20), "COSECHADO"),
            ("Frutilla", hoy - timedelta(days=15), hoy + timedelta(days=45), "EN_CRECIMIENTO"),
        ]

        for nombre, siembra, cosecha, estado in ciclos_data:
            CicloCultivo.objects.get_or_create(
                especie=especies[nombre],
                fecha_siembra=siembra,
                defaults={
                    "fecha_cosecha_estimada": cosecha,
                    "estado": estado,
                    "observaciones": f"Ciclo de prueba para {nombre.lower()}.",
                },
            )

        self.stdout.write("Creando actividades...")

        actividades_data = [
            ("Jornada de siembra de primavera", hoy + timedelta(days=5), time(10, 0), "Huerto principal", 2, admin1, "PROGRAMADA"),
            ("Taller de compostaje", hoy + timedelta(days=12), time(15, 30), "Sala multiuso CEA", 10, admin2, "PROGRAMADA"),
            ("Mantencion de cultivos de invierno", hoy - timedelta(days=8), time(9, 0), "Huerto secundario", 6, admin1, "FINALIZADA"),
            ("Cosecha comunitaria", hoy + timedelta(days=25), time(11, 0), "Huerto principal", 15, admin2, "PROGRAMADA"),
        ]

        actividades = {}
        for titulo, fecha, hora, lugar, cupo, responsable, estado in actividades_data:
            actividad, _ = Actividad.objects.get_or_create(
                titulo=titulo,
                fecha=fecha,
                defaults={
                    "descripcion": f"Actividad comunitaria: {titulo.lower()}.",
                    "hora": hora,
                    "lugar": lugar,
                    "cupo_maximo": cupo,
                    "responsable": responsable,
                    "estado": estado,
                },
            )
            actividades[titulo] = actividad

        self.stdout.write("Creando inscripciones (incluye una actividad con cupo lleno)...")

        # "Jornada de siembra de primavera" tiene cupo_maximo=2: la llenamos para
        # poder probar el bloqueo de cupo maximo (RF-06) en vivo.
        inscripciones_plan = [
            ("Jornada de siembra de primavera", voluntarios[0], "CONFIRMADA", False),
            ("Jornada de siembra de primavera", voluntarios[1], "CONFIRMADA", False),
            ("Taller de compostaje", voluntarios[0], "CONFIRMADA", False),
            ("Taller de compostaje", voluntarios[2], "CONFIRMADA", False),
            ("Taller de compostaje", voluntarios[3], "EN_ESPERA", False),
            ("Mantencion de cultivos de invierno", voluntarios[1], "CONFIRMADA", True),
            ("Mantencion de cultivos de invierno", voluntarios[4], "CONFIRMADA", False),
            ("Cosecha comunitaria", voluntarios[2], "CONFIRMADA", False),
            ("Cosecha comunitaria", voluntarios[3], "CANCELADA", False),
        ]

        for titulo, voluntario, estado, asistio in inscripciones_plan:
            Inscripcion.objects.get_or_create(
                actividad=actividades[titulo],
                voluntario=voluntario,
                defaults={"estado": estado, "asistio": asistio},
            )

        self.stdout.write(self.style.SUCCESS("Datos de prueba cargados correctamente."))
        if credenciales:
            self.stdout.write(self.style.WARNING(
                "Credenciales generadas (copialas ahora, no se guardan en ningun lado):"
            ))
            for username, pw, rol in credenciales:
                self.stdout.write(f"  {username} / {pw}  ({rol})")
        else:
            self.stdout.write("Los usuarios ya existian, no se generaron contrasenas nuevas.")
