import logging

from django.contrib.auth import get_user_model, user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver

from user_secrets.caches import delete_user_itermediate_secret, set_user_itermediate_secret
from user_secrets.crypto import Cryptor
from user_secrets.exceptions import DecryptError
from user_secrets.user_key import get_user_key


log = logging.getLogger(__name__)
UserModel = get_user_model()


@receiver(user_logged_in)
def user_logged_in_callback(*, sender, request, user, **kwargs):
    log.debug('User logged in')

    encrypted_secret = user.encrypted_secret
    if not encrypted_secret:
        log.info(f'No encrypted_secret for user {user.pk}')
        delete_user_itermediate_secret(user=user)  # Maybe in cache exists outdated information!
        return

    # Set in UserSecretsAuthBackend.authenticate():
    fernet_key = get_user_key()

    try:
        itermediate_secret = Cryptor(fernet_key=fernet_key).decrypt(encrypted_data=user.encrypted_secret)
    except DecryptError:
        # secret can't be decrypted
        # e.g.: password changed without update the encrypted_secret or SECRET_KEY changed?
        log.error('Decrypt itermediate secret failed!')
    else:
        set_user_itermediate_secret(
            user=user,
            itermediate_secret=itermediate_secret
        )


@receiver(user_logged_out)
def user_logged_out_callback(*, sender, request, user, **kwargs):
    log.debug('User logged out')
    delete_user_itermediate_secret(user=user)


@receiver(user_login_failed)
def user_login_failed_callback(*, sender, credentials, request, **kwargs):
    log.debug('User login failed -> set request.fernet = None')
    if request:
        request.fernet = None
    print(sender, credentials, request)
