from .base_settings import *  # noqa: F401,F403

# Always use the console backend locally so verification codes show up in the terminal.
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
