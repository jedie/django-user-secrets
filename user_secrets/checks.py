from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.checks import Error, Tags, register

from user_secrets.models import AbstractUserSecretsModel


UserModel = get_user_model()


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

    if not issubclass(UserModel, AbstractUserSecretsModel):
        errors.append(
            Error(
                (
                    f'Current user model {UserModel.__module__}.{UserModel.__name__} is not a'
                    f' subclass of {AbstractUserSecretsModel.__module__}.{AbstractUserSecretsModel.__name__}'
                ),
                id='user_secrets.E003',
            )
        )

    return errors
