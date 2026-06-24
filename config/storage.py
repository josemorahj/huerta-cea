import os
from django.contrib.staticfiles.storage import StaticFilesStorage
from whitenoise.compress import Compressor


class SequentialCompressedStaticFilesStorage(StaticFilesStorage):
    """
    Storage que copia estáticos y los comprime secuencialmente
    (sin ThreadPoolExecutor) para evitar race conditions en Python 3.14+.
    """
    def post_process(self, paths, dry_run=False, **options):
        if dry_run:
            return

        extensions = getattr(self, "WHITENOISE_SKIP_COMPRESS_EXTENSIONS", None)
        from django.conf import settings
        extensions = getattr(settings, "WHITENOISE_SKIP_COMPRESS_EXTENSIONS", extensions)
        compressor = Compressor(extensions=extensions, quiet=True)

        for path in paths:
            if compressor.should_compress(path):
                full_path = self.path(path)
                if not os.path.exists(full_path):
                    continue
                prefix_len = len(full_path) - len(path)
                try:
                    for compressed_path in compressor.compress(full_path):
                        compressed_name = compressed_path[prefix_len:]
                        yield path, compressed_name, True
                except (FileNotFoundError, OSError):
                    continue
