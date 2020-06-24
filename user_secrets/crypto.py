import base64
import logging
import secrets

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from django.conf import settings
from django.core.cache import caches

from user_secrets.constants import ENCRYPTED_SECRET_LENGTH


log = logging.getLogger(__name__)


CACHE_PATTERN = 'raw_user_token_{user_pk}'


class CryptoError(Exception):
    pass


def get_cache_key(user):
    key = CACHE_PATTERN.format(user_pk=user.pk)
    return key


def set_user_raw_user_token(*, user, raw_user_token):
    log.debug(f'Save raw_user_token to cache for user: {user.pk}')
    cache = caches['user_secrets']
    cache_key = get_cache_key(user=user)
    cache.set(cache_key, raw_user_token)


def get_user_raw_user_token(*, user):
    log.debug(f'Get raw_user_token from cache for user: {user.pk}')
    cache = caches['user_secrets']
    cache_key = get_cache_key(user=user)
    return cache.get(cache_key)


def delete_user_raw_user_token(*, user):
    log.debug(f'Delete raw_user_token from cache for user: {user.pk}')
    cache = caches['user_secrets']
    cache_key = get_cache_key(user=user)
    cache.delete(cache_key)


def fernet_from_password(*, raw_password):
    """
    Used on login to generate the temporary Fernet() instance
    from the plain-text user password.
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=settings.SECRET_KEY.encode('ASCII', errors='strict'),
        iterations=10000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(raw_password.encode('ASCII', errors='strict')))
    fernet = Fernet(key)
    log.debug(f'temporary Fernet() instance generated: {fernet}')
    return fernet


def generate_raw_user_token():
    raw_user_token = secrets.token_bytes(nbytes=ENCRYPTED_SECRET_LENGTH)
    return raw_user_token


def fernet_encrypt(fernet, data):
    """
    Encrypt data via fernet and return the base64 result as a string (not bytes)
    """
    assert isinstance(fernet, Fernet)
    assert isinstance(data, bytes)
    encrypted_data = fernet.encrypt(data)  # URL-safe base64-encoded bytes
    return encrypted_data.decode('ASCII', errors='strict')


def fernet_decrypt(fernet, encrypted_data):
    """
    Decrypt data via fernet and return the base64 result as bytes
    """
    assert isinstance(fernet, Fernet)
    if not isinstance(encrypted_data, bytes):
        encrypted_data = encrypted_data.encode('ASCII', errors='strict')
    raw_data = fernet.decrypt(encrypted_data)
    return raw_data


def encrypt_user_raw_user_token(*, raw_user_token, raw_password):
    """
    Encrypt 'raw_user_token' with the plain-text user password.
    """
    assert isinstance(raw_user_token, bytes)
    encrypted_secret = fernet_encrypt(
        fernet=fernet_from_password(raw_password=raw_password),
        data=raw_user_token
    )
    return encrypted_secret


def decrypt_user_raw_user_token(*, encrypted_secret, raw_password):
    """
    Decrypt the "encrypted_secret" with the plain-text user password.
    """
    encrypted_secret = encrypted_secret.encode('ASCII', errors='strict')  # base64 string to bytes
    fernet = fernet_from_password(raw_password=raw_password)
    raw_user_token = fernet.decrypt(encrypted_secret)
    return raw_user_token


def encrypt(*, user, data):
    """
    Encrypt 'data' for the 'user'.
    return the base64 result as a string (not bytes)
    """
    raw_user_token = get_user_raw_user_token(user=user)
    if raw_user_token is None:
        raise CryptoError('No raw_user_token')

    assert isinstance(raw_user_token, bytes)
    return fernet_encrypt(
        fernet=Fernet(raw_user_token),
        data=data,
    )
