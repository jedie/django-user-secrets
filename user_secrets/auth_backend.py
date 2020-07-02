import logging

from user_secrets.crypto import secret2fernet_key
from user_secrets.user_key import set_user_key


log = logging.getLogger(__name__)


class UserSecretsAuthBackend:
    def authenticate(self, request, username=None, password=None):
        if password and request:
            log.debug('create fernet key from password')
            fernet_key = secret2fernet_key(secret=password)

            # Save for: user_secrets.signals.user_logged_in_callback
            set_user_key(fernet_key)

        return None
