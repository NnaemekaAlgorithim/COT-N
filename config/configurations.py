from decouple import Csv, config

BASE_PREFIX = config('BASE_PREFIX', default='dev')
DEBUG = config('DEBUG', default=True, cast=bool)
SECRET_KEY = config('SECRET_KEY', default='')
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='127.0.0.1', cast=Csv())

DB_HOST_NAME = config('DB_HOST_NAME', default='')
DB_PORT = config('DB_PORT', default='')
DB_NAME = config('DB_NAME', default='')
DB_USER_NAME = config('DB_USER_NAME', default='')
DB_PASSWORD = config('DB_PASSWORD', default='')
DATABASE_URL = config(
    'DATABASE_URL',
    default=f'postgresql://{DB_USER_NAME}:{DB_PASSWORD}@{DB_HOST_NAME}:{DB_PORT}/{DB_NAME}',
)

PAYSTACK_SECRET_KEY = config('PAYSTACK_SECRET_KEY', default='')
PAYSTACK_PUBLIC_KEY = config('PAYSTACK_PUBLIC_KEY', default='')
PAYSTACK_BASE_URL = config('PAYSTACK_BASE_URL', default='https://api.paystack.co')

EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='no-reply@cot-n.local')

