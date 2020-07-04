import logging
import warnings
from pathlib import Path

# https://github.com/jedie/django-tools
from django_tools.unittest_utils.logging_utils import CutPathnameLogRecordFactory, FilterAndLogWarnings


print('Use settings:', __file__)


###############################################################################
# Settings for django-user-secrets usage:


# The SECRET_KEY should never changed after django-user-secrets are created!
SECRET_KEY = 'This is not a secret! But this is only the DEMO ;)'


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
    'default': {  # Can use any backend.
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'default',
    },
    'user_secrets': {  # Should be use the LocMemCache!
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

    'user_secrets.middleware.UserSecretsMiddleware',  # inserted after AuthenticationMiddleware
)


ROOT_URLCONF = 'user_secrets_tests.urls'


###############################################################################
# Following settings are not really relevant to django-user-secret!


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = Path(__file__).parent


DEBUG = True


INTERNAL_IPS = ['127.0.0.1']


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


ALLOWED_HOSTS = ['*']  # Allow any domain/subdomain


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': str(Path(BASE_DIR.parent, 'test_project_db.sqlite3')),
    }
}


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = str(Path(BASE_DIR, 'static'))
assert str(STATIC_ROOT).endswith('/user_secrets_tests/static')

MEDIA_URL = '/media/'
MEDIA_ROOT = str(Path(BASE_DIR, 'media'))
assert str(MEDIA_ROOT).endswith('/user_secrets_tests/media')


LOGIN_URL = '/admin/login/'
LOGIN_REDIRECT_URL = '/'

PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',  # Speedup tests
)


###############################################################################
# setup logging


# Adds 'cut_path' attribute on log record. So '%(cut_path)s' can be used in log formatter.
# user_secrets.unittest_utils.logging_utils.CutPathnameLogRecordFactory
logging.setLogRecordFactory(CutPathnameLogRecordFactory(max_length=50))


# Filter warnings and pipe them to logging system:
# user_secrets.unittest_utils.logging_utils.FilterAndLogWarnings
warnings.showwarning = FilterAndLogWarnings()


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
