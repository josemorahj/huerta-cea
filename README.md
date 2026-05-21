# Huerta CEA

**Plataforma de gestion para la Huerta Comunitaria del Centro Educativo Ambiental (CEA)**
*Municipalidad de Santiago, Chile*

Sistema web desarrollado para centralizar y digitalizar la operacion de la huerta comunitaria del CEA, reemplazando los registros manuales y la coordinacion informal por canales de mensajeria. La plataforma permite la administracion de especies cultivables, planificacion de ciclos de siembra y cosecha, organizacion de actividades comunitarias con inscripcion de voluntarios, y generacion de indicadores de gestion para el equipo coordinador.

---

## Stack tecnologico

| Componente | Tecnologia |
|---|---|
| **Backend** | Python 3.14+ / Django 6.0.4 |
| **API** | Django REST Framework + SimpleJWT (autenticacion JWT) |
| **Base de datos** | SQLite3 (desarrollo) / PostgreSQL via Supabase (produccion) |
| **Frontend** | Django Templates (server-side rendering) + Bootstrap |
| **Almacenamiento multimedia** | Cloudinary (produccion) / ImageField local (desarrollo) |
| **Archivos estaticos** | WhiteNoise |
| **Despliegue** | Render (Web Service + PostgreSQL) |
| **ORM** | Django ORM con modelo de usuario personalizado (AUTH_USER_MODEL) |

### Dependencias principales

```
Django==6.0.4
djangorestframework==3.17.1
djangorestframework_simplejwt==5.5.1
django-cors-headers==4.9.0
django-cloudinary-storage==0.3.0
cloudinary==1.44.2
gunicorn==25.3.0
psycopg2-binary==2.9.12
whitenoise==6.12.0
python-decouple==3.8
pillow==12.2.0
dj-database-url==2.3.0
```

---

## Arquitectura del sistema

El proyecto se estructura en cuatro aplicaciones Django, cada una con responsabilidades claramente delimitadas:

### `accounts` — Autenticacion y roles
Modelo de usuario personalizado (`User`) que extiende `AbstractUser` con los campos `rol` (admin/voluntario) y `telefono`. Implementa registro, inicio de sesion y cierre de sesion con redireccion condicional segun el rol del usuario autenticado.

### `crops` — Catalogo de especies y calendario de cultivos
Dos modelos principales:
- **`Especie`**: Repositorio maestro de fichas tecnicas con datos como nombre comun/cientifico, descripcion, condiciones de cultivo, frecuencia de riego, temporada recomendada e imagen referencial.
- **`CicloCultivo`**: Instancia real de siembra asociada a una especie, con fechas de siembra y cosecha estimada, estado del ciclo (sembrado, en crecimiento, listo para cosecha, cosechado) y observaciones. Incluye validacion a nivel de modelo que impide fechas de cosecha anteriores a la siembra.

### `activities` — Actividades comunitarias e inscripciones
Dos modelos principales:
- **`Actividad`**: Evento programado con titulo, descripcion, fecha, hora, lugar, cupo maximo, responsable y estado.
- **`Inscripcion`**: Relacion muchos-a-muchos entre voluntarios y actividades, con validacion de unicidad (no duplicados) y control de cupo maximo. Incluye campo `asistio` para registro de asistencia.

### `dashboard` — Panel de metricas
Vista protegida para administradores que presenta indicadores clave: total de voluntarios registrados, actividades programadas en el mes y cultivos activos en la huerta.

---

## Funcionalidades por rol

### Administrador

| Funcionalidad | Ruta | Descripcion |
|---|---|---|
| **Dashboard** | `/dashboard/` | Panel con metricas: total voluntarios, actividades del mes, cultivos activos |
| **Admin Django** | `/admin/` | CRUD completo de especies, ciclos de cultivo, actividades, inscripciones y usuarios |
| **Gestion de especies** | `/admin/crops/especie/` | Alta, baja y modificacion del catalogo de especies con imagenes |
| **Planificacion de cultivos** | `/admin/crops/ciclocultivo/` | Registro de siembras con fechas, estados y observaciones |
| **Gestion de actividades** | `/admin/activities/actividad/` | Creacion y edicion de actividades comunitarias |
| **Control de inscripciones** | `/admin/activities/inscripcion/` | Visualizacion, edicion y marcado de asistencia de voluntarios |
| **Fichas de cultivo** | `/crops/fichas/` | Catalogo publico de especies con buscador y filtro por temporada |
| **Calendario** | `/crops/calendario/` | Visualizacion de ciclos de cultivo del mes actual |

### Voluntario

| Funcionalidad | Ruta | Descripcion |
|---|---|---|
| **Registro** | `/accounts/registro/` | Creacion de cuenta con rol voluntario por defecto |
| **Actividades disponibles** | `/activities/` | Listado de actividades programadas y pasadas |
| **Inscripcion** | (boton en cada actividad) | Inscripcion a actividades con validacion de cupo |
| **Historial personal** | `/activities/mi-historial/` | Registro completo de inscripciones propias |
| **Fichas de cultivo** | `/crops/fichas/` | Consulta del catalogo de especies |
| **Calendario** | `/crops/calendario/` | Visualizacion del calendario de cultivos |

---

## Instalacion y ejecucion local

### Requisitos previos

- Python 3.14 o superior
- pip
- Git

### Pasos

```bash
# 1. Clonar el repositorio
git clone https://github.com/josemorahj/huerta-cea.git
cd huerta-cea

# 2. Crear y activar entorno virtual
# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate

# Linux / macOS / Git Bash
python3 -m venv venv
source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Aplicar migraciones
python manage.py migrate

# 5. (Opcional) Cargar datos de ejemplo
python manage.py loaddata crops/fixtures/especies_iniciales.json

# 6. (Opcional) Crear superusuario
python manage.py crear_superusuario

# 7. Iniciar servidor de desarrollo
python manage.py runserver

# 8. Abrir en el navegador
# http://127.0.0.1:8000
```

---

## Variables de entorno

El proyecto utiliza `python-decouple` para la gestion de configuracion. Crear un archivo `.env` en la raiz del proyecto con las siguientes variables:

```env
# Django
SECRET_KEY=django-insecure-6c3+k)37it6%^ub@ro-x&v^gcbrzr#awcb_r59m0+cw-dl^ye6
DEBUG=True
ALLOWED_HOSTS=*

# Base de datos (omitir para usar SQLite3 local)
DATABASE_URL=postgres://usuario:password@host:5432/huerta-cea

# Cloudinary (opcional en desarrollo; necesario para imagenes en produccion)
CLOUDINARY_CLOUD_NAME=mi-cloud
CLOUDINARY_API_KEY=123456789
CLOUDINARY_API_SECRET=abc123def456
```

> **Nota**: En desarrollo con `DEBUG=True`, las imagenes se sirven localmente. Solo se requiere Cloudinary en produccion.

---

## Ejecucion de tests

### Todos los tests

```bash
python manage.py test
```

### Tests especificos por modulo

```bash
# Autenticacion y roles (20 tests)
python manage.py test accounts

# Actividades e inscripciones
python manage.py test activities

# Catalogo de especies
python manage.py test crops

# Dashboard
python manage.py test dashboard
```

### Tests con cobertura

```bash
# Instalar coverage (ya incluido en el entorno)
pip install coverage

# Ejecutar tests con medicion de cobertura
coverage run --source='.' manage.py test

# Ver reporte en consola
coverage report

# Ver reporte con lineas no cubiertas
coverage report --show-missing

# Generar reporte HTML (abrir htmlcov/index.html)
coverage html
```

### Tests unitarios implementados (24 tests)

| Modulo | Tests | Cobertura |
|---|---|---|
| `accounts` | Registro, login, logout, redireccion por rol | ~99% |
| `activities` | Inscripcion duplicada, cupo maximo | ~69% |
| `crops` | Busqueda por nombre, busqueda sin resultados | ~46% |

---

## Produccion

La plataforma se encuentra desplegada en Render:

**https://huerta-cea.onrender.com**

### Infraestructura

- **Web Service**: Render (Gunicorn + WhiteNoise)
- **Base de datos**: PostgreSQL gestionada mediante Supabase (Session Pooler)
- **Almacenamiento multimedia**: Cloudinary (imagenes de especies)
- **Archivos estaticos**: WhiteNoise con compresion y cacheo

### Variables de entorno requeridas en produccion

| Variable | Valor | Proposito |
|---|---|---|
| `DATABASE_URL` | `postgres://...` | Conexion a PostgreSQL |
| `SECRET_KEY` | Clave generada segura | Firma de sesiones y tokens |
| `DEBUG` | `False` | Deshabilitar modo debug |
| `ALLOWED_HOSTS` | `.onrender.com` | Hosts permitidos |
| `CLOUDINARY_CLOUD_NAME` | (segun cuenta) | Almacenamiento de imagenes |
| `CLOUDINARY_API_KEY` | (segun cuenta) | Autenticacion Cloudinary |
| `CLOUDINARY_API_SECRET` | (segun cuenta) | Autenticacion Cloudinary |

---

## Estado del proyecto

### Completado

- Sprint 1: Estructura base del proyecto, modelos, URLs, templates y autenticacion con roles
- Sprint 2: Modelos Especie y CicloCultivo con administracion en Django Admin
- Sprint 3: Fichas de cultivo publicas con buscador, detalle de especie y calendario
- Sprint 4: Actividades comunitarias, inscripciones, dashboard con metricas y registro de asistencia
- Sprint 5: Tests automatizados (24 tests), preparacion para despliegue
- Despliegue: Produccion activa en Render con Supabase + Cloudinary

### Pendientes

- Notificaciones por correo electronico a voluntarios al inscribirse
- Panel de reportes exportables (CSV/PDF)
- Perfil de usuario editable con foto y preferencias
- Sistema de recordatorios para actividades proximas

---

## Licencia

Proyecto academico desarrollado en el contexto del Centro Educativo Ambiental (CEA) - Municipalidad de Santiago.
