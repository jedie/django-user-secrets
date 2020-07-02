import logging
import warnings
from pathlib import Path

# https://github.com/jedie/django-tools
from django_tools.unittest_utils.logging_utils import CutPathnameLogRecordFactory, FilterAndLogWarnings


print('Use settings:', __file__)

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = Path(__file__).parent

DEBUG = True
INTERNAL_IPS = ['127.0.0.1']

SECRET_KEY = 'This is not a secret! But this is only the DEMO ;)'
ALLOWED_HOSTS = ['*']  # Allow any domain/subdomain

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': str(Path(BASE_DIR.parent, 'test_project_db.sqlite3')),
    }
}

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # django-user-secrets:
    'user_secrets.apps.UserSecretsConfig',

    # The Test app:
    'user_secrets_tests.apps.UserSecretsTestAppConfig',

    'debug_toolbar',
)

AUTH_USER_MODEL = 'user_secrets.UserSecrets'
AUTHENTICATION_BACKENDS = [
    'user_secrets.auth_backend.UserSecretsAuthBackend',  # Must be at first
    'django.contrib.auth.backends.ModelBackend'
]
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'default',
    },
    'user_secrets': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'user_secrets',
    }
}

MIDDLEWARE = (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [Path(BASE_DIR, 'templates')],
        'OPTIONS': {
            "loaders": [
                (
                    "django_tools.template.loader.DebugCacheLoader",
                    (
                        "django.template.loaders.filesystem.Loader",
                        "django.template.loaders.app_directories.Loader"
                    ),
                )
            ],
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    }
]

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# ==============================================================================

EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# ==============================================================================

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = str(Path(BASE_DIR, 'static'))
assert str(STATIC_ROOT).endswith('/user_secrets_tests/static')

MEDIA_URL = '/media/'
MEDIA_ROOT = str(Path(BASE_DIR, 'media'))
assert str(MEDIA_ROOT).endswith('/user_secrets_tests/media')

# ==============================================================================


ROOT_URLCONF = 'user_secrets_tests.urls'

LOGIN_URL = '/admin/login/'  # TODO: Build own login view

PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',  # Speedup tests
)

# _____________________________________________________________________________

# Adds 'cut_path' attribute on log record. So '%(cut_path)s' can be used in log formatter.
# user_secrets.unittest_utils.logging_utils.CutPathnameLogRecordFactory
logging.setLogRecordFactory(CutPathnameLogRecordFactory(max_length=50))

# Filter warnings and pipe them to logging system:
# user_secrets.unittest_utils.logging_utils.FilterAndLogWarnings
warnings.showwarning = FilterAndLogWarnings()

# -----------------------------------------------------------------------------

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'colored': {  # https://github.com/borntyping/python-colorlog
            '()': 'colorlog.ColoredFormatter',
            #
            # https://docs.python.org/3/library/logging.html#logrecord-attributes
            'format': '%(log_color)s%(asctime)s %(levelname)8s %(cut_path)s:%(lineno)-3s %(name)s %(message)s',
        }
    },
    'handlers': {'console': {'class': 'colorlog.StreamHandler', 'formatter': 'colored'}},
    'loggers': {
        'django': {'handlers': ['console'], 'level': 'WARNING', 'propagate': False},
        'django.request': {'handlers': ['console'], 'level': 'DEBUG', 'propagate': False},
        'user_secrets': {'handlers': ['console'], 'level': 'DEBUG', 'propagate': False},
    },
}
