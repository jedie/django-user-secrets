import base64
import datetime
import logging

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from django.conf import settings
from django.contrib.auth.hashers import get_random_string
from django.utils import timezone

from user_secrets.caches import get_user_itermediate_secret
from user_secrets.constants import ITERMEDIATE_SECRET_LENGTH
from user_secrets.exceptions import DecryptError, NoUserItermediateSecretError


log = logging.getLogger(__name__)


def secret2fernet_key(*, secret):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=settings.SECRET_KEY.encode('ASCII', errors='strict'),
        iterations=10000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(secret.encode('utf-8')))
    return key


class Cryptor:
    def __init__(self, secret=None, fernet_key=None):
        if secret is not None:
            assert fernet_key is None
            assert isinstance(secret, str)
            self.fernet = self._secret2fernet(secret=secret)
        else:
            assert fernet_key is not None
            assert isinstance(fernet_key, bytes)
            self.fernet = Fernet(fernet_key)

    def _secret2fernet(self, secret):
        key = secret2fernet_key(secret=secret)
        fernet = Fernet(key)
        return fernet

    def encrypt(self, *, data):
        assert isinstance(data, str)
        encrypted_data = self.fernet.encrypt(data.encode('utf-8'))
        return encrypted_data.decode('ASCII', errors='strict')

    def decrypt(self, *, encrypted_data):
        assert isinstance(encrypted_data, str)
        try:
            data = self.fernet.decrypt(encrypted_data.encode('ASCII', errors='strict'))
        except InvalidToken:
            # e.g.: password change without update or SECRET_KEY changed?
            log.error('Decrypt error: Invalid token!')
            raise DecryptError()

        return data.decode('utf-8')

    def extract_timestamp(self, *, encrypted_data):
        if encrypted_data is None:
            return

        assert isinstance(encrypted_data, str)
        try:
            return self.fernet.extract_timestamp(encrypted_data.encode('ASCII', errors='strict'))
        except InvalidToken:
            return

    def get_datetime(self, *, encrypted_data):
        timestamp = self.extract_timestamp(encrypted_data=encrypted_data)
        if not timestamp:
            return

        tz = timezone.get_current_timezone()
        dt = datetime.datetime.fromtimestamp(timestamp, tz=tz)
        return dt


def encrypt_itermediate_secret(*, itermediate_secret, raw_password):
    encrypted_itermediate_secret = Cryptor(secret=raw_password).encrypt(data=itermediate_secret)
    return encrypted_itermediate_secret


def generate_encrypted_secret(*, raw_password):
    itermediate_secret = get_random_string(ITERMEDIATE_SECRET_LENGTH)
    encrypted_itermediate_secret = encrypt_itermediate_secret(
        itermediate_secret=itermediate_secret,
        raw_password=raw_password
    )
    return itermediate_secret, encrypted_itermediate_secret


def user_encrypt(*, user, data):
    itermediate_secret = get_user_itermediate_secret(user=user)
    if itermediate_secret is None:
        log.error('Itermediate secret missing for user: %s', user.pk)
        raise NoUserItermediateSecretError()

    return Cryptor(secret=itermediate_secret).encrypt(data=data)


def user_decrypt(*, user, encrypted_data):
    itermediate_secret = get_user_itermediate_secret(user=user)
    if itermediate_secret is None:
        log.error('Itermediate secret missing for user: %s', user.pk)
        raise NoUserItermediateSecretError()

    return Cryptor(secret=itermediate_secret).decrypt(encrypted_data=encrypted_data)


def user_get_datetime(*, user, encrypted_data):
    itermediate_secret = get_user_itermediate_secret(user=user)
    if itermediate_secret is None:
        log.error('Itermediate secret missing for user: %s', user.pk)
        return

    return Cryptor(secret=itermediate_secret).get_datetime(encrypted_data=encrypted_data)
