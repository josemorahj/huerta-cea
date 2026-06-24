release: python collectstatic_fix.py
web: gunicorn config.wsgi --log-file -
# Nota: collectstatic_fix.py es un workaround para bug de Django 6.0.4
# que causa collectstatic --noinput copie 0 archivos al usar nuestro
# backend personalizado SequentialCompressedStaticFilesStorage.

