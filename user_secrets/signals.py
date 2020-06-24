import logging

from django.contrib.auth import get_user_model, user_logged_in, user_logged_out, user_login_failed
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from user_secrets.crypto import delete_user_raw_user_token, fernet_decrypt, set_user_raw_user_token


log = logging.getLogger(__name__)
UserModel = get_user_model()


@receiver(user_logged_in)
def user_logged_in_callback(*, sender, request, user, **kwargs):
    log.debug('User logged in')
    print(sender, request, user)

    encrypted_secret = user.encrypted_secret
    if not encrypted_secret:
        log.info(f'No encrypted_secret for user {user.pk}')
        return

    fernet = getattr(request, 'fernet')
    if fernet is None:
        log.warning(f'request.fernet is None')
        return

    log.debug('Set request.fernet = None')
    request.fernet = None

    raw_user_token = fernet_decrypt(
        fernet=fernet,
        encrypted_data=encrypted_secret
    )
    set_user_raw_user_token(
        user=user,
        raw_user_token=raw_user_token
    )


@receiver(user_logged_out)
def user_logged_out_callback(*, sender, request, user, **kwargs):
    log.debug('User logged out')
    delete_user_raw_user_token(user=user)


@receiver(user_login_failed)
def user_login_failed_callback(*, sender, credentials, request, **kwargs):
    log.debug('User login failed -> set request.fernet = None')
    if request:
        request.fernet = None
    print(sender, credentials, request)


@receiver(post_save, sender=UserModel)
def user_model_post_save_callback(sender, instance, created, **kwargs):
    print("user_model_post_save_callback", sender, instance, created)


@receiver(post_delete, sender=UserModel)
def user_model_post_delete_callback(sender, **kwargs):
    print("user_model_post_delete_callback", sender, kwargs)
