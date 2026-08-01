import dj_database_url

from .base_settings import *  # noqa: F401,F403

DATABASES = {
    'default': dj_database_url.parse(DATABASE_URL)
}

# Served by the shared nginx container under its /cotn/ location block.
STATIC_URL = '/cotn/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/cotn/media/'
MEDIA_ROOT = BASE_DIR / 'mediafiles'
