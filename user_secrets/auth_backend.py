import base64
import logging

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from django.conf import settings


log = logging.getLogger(__name__)


class UserSecretsAuthBackend:
    """
    Generate the temporary Fernet() instance from the plain-text user password.
    This will only exists in RAM and never saved persistent.
    """

    def authenticate(self, request, username=None, password=None):
        if password and request:
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=(settings.SECRET_KEY).encode(),
                iterations=10000,
                backend=default_backend()
            )
            key = base64.urlsafe_b64encode(kdf.derive((password).encode()))
            fernet = Fernet(key)
            request.fernet = fernet
            log.debug(f'Add request.fernet="{fernet}"')

        return None
