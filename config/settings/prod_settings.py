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

# nginx strips the /cotn prefix before forwarding, so urlpatterns stay unprefixed;
# this makes reverse()/build_absolute_uri()/pagination/schema links re-add it correctly.
FORCE_SCRIPT_NAME = '/cotn'

