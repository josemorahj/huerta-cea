# Huerta CEA

Plataforma de gestion de la Huerta Comunitaria del Centro Educativo Ambiental (CEA) - Municipalidad de Santiago.

## Requisitos

- Python 3.14+
- pip

## Instalacion y ejecucion local

1. Clonar el repositorio y entrar al directorio:

`ash
cd huerta-cea
`

2. Activar el entorno virtual:

`ash
# Windows (PowerShell)
.\\venv\\Scripts\\Activate

# Linux / macOS / Git Bash
source venv/bin/activate
`

3. Instalar dependencias:

`ash
pip install -r requirements.txt
`

4. Aplicar migraciones:

`ash
python manage.py migrate
`

5. Iniciar el servidor de desarrollo:

`ash
python manage.py runserver
`

6. Abrir en el navegador: http://127.0.0.1:8000

## Ejecutar tests

`ash
python manage.py test
`

Para un test especifico:

`ash
python manage.py test accounts.tests.AccesoDashboardTest
python manage.py test activities.tests.InscripcionDuplicadaTest
python manage.py test crops.tests.BuscadorFichasTest
`

## Proximos pasos (pendientes para produccion)

- [ ] **PostgreSQL en Render**: Migrar de SQLite3 a PostgreSQL configurando DATABASE_URL como variable de entorno en Render.
- [ ] **Redireccion raiz**: La vista home_view redirige segun rol; en servidores sin autenticacion inicial, asegurar que la raiz funcione correctamente con DEBUG=False.
- [ ] **Media en produccion**: Las imagenes subidas (ImageField en Especie) requieren un servicio de almacenamiento como AWS S3 o Django storages configurado con el bucket de Render. Actualmente solo funcionan en desarrollo con DEBUG=True.
- [ ] **Staticfiles**: Ejecutar python manage.py collectstatic antes del deploy y verificar que WhiteNoise sirva los archivos estaticos correctamente.

## Despliegue en Render

1. Crear un Web Service en Render conectado al repositorio de GitHub.
2. Configurar:
   - **Build Command**: pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
   - **Start Command**: gunicorn config.wsgi --log-file -
3. Agregar variables de entorno en Render:
   - DATABASE_URL: URL de la base de datos PostgreSQL (crear una desde el dashboard de Render).
   - SECRET_KEY: Clave secreta de Django (generar una nueva para produccion).
   - DEBUG: False
   - ALLOWED_HOSTS: .onrender.com
