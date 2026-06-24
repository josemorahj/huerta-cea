"""
Script para hacer collectstatic manualmente, usado como workaround
porque collectstatic de Django 6.0.4 parece tener un bug con ciertas
configuraciones de storage.

Uso: python collectstatic_fix.py
"""
import os
import shutil
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django
django.setup()

from django.conf import settings
from django.contrib.staticfiles import finders
from whitenoise.compress import Compressor

STATIC_ROOT = str(settings.STATIC_ROOT)


def collect_static():
    """Copia archivos estaticos de todos los finders a STATIC_ROOT."""
    if os.path.exists(STATIC_ROOT):
        shutil.rmtree(STATIC_ROOT)

    copied = 0
    errors = []
    seen = set()

    for finder in finders.get_finders():
        for path, src_storage in finder.list([]):
            if path in seen:
                continue
            seen.add(path)

            src_path = src_storage.path(path)
            dest_path = os.path.join(STATIC_ROOT, path)
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)

            try:
                shutil.copy2(src_path, dest_path)
                copied += 1
            except Exception as e:
                errors.append((path, str(e)))

    print(f"Copied {copied} static files to {STATIC_ROOT}")
    if errors:
        print(f"\n{len(errors)} errors:")
        for path, err in errors[:5]:
            print(f"  - {path}: {err}")

    # Compress files using whitenoise compressor
    print("\nCompressing static files...")
    compressor = Compressor(quiet=False)
    compressed = 0
    for root, dirs, files in os.walk(STATIC_ROOT):
        for fname in files:
            fpath = os.path.join(root, fname)
            relpath = os.path.relpath(fpath, STATIC_ROOT)
            if compressor.should_compress(relpath):
                try:
                    for compressed_path in compressor.compress(fpath):
                        print(f"  Compressed: {os.path.relpath(compressed_path, STATIC_ROOT)}")
                        compressed += 1
                except Exception as e:
                    print(f"  Failed to compress {relpath}: {e}")

    print(f"Compressed {compressed} files")
    return copied


if __name__ == "__main__":
    count = collect_static()
    sys.exit(0 if count > 0 else 1)
