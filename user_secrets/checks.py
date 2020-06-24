from django.conf import settings
from django.core.checks import Error, Tags, register


@register(Tags.translation)
def user_secrets_settings_check(app_configs, **kwargs):
    errors = []
    cache = settings.CACHES.get('user_secrets')
    if not cache:
        errors.append(
            Error(
                'No "user_secrets" settings.CACHES defined!',
                id='user_secrets.E001',
            )
        )
    elif not cache['BACKEND'].endswith('LocMemCache'):
        errors.append(
            Error(
                'settings.CACHES["user_secrets"] is no "LocMemCache" !',
                id='user_secrets.E002',
            )
        )
    return errors
