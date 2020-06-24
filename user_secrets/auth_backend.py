import logging

from user_secrets.crypto import fernet_from_password


log = logging.getLogger(__name__)


class UserSecretsAuthBackend:
    """
    Generate the temporary Fernet() instance from the plain-text user password.
    This will only exists in RAM and never saved persistent.
    """

    def authenticate(self, request, username=None, password=None):
        if password and request:
            fernet = fernet_from_password(raw_password=password)
            request.fernet = fernet
            log.debug(f'Add request.fernet="{fernet}"')

        return None
