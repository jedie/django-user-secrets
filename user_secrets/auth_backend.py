import hashlib
import logging

from django.conf import settings


log = logging.getLogger(__name__)


class UserSecretsAuthBackend:
    """
    Generate the Temporary hash of the plain-text user password.
    This hash will only exists in RAM and never saved persistent.
    """

    def authenticate(self, request, username=None, password=None):
        if password:
            temp_token = hashlib.sha3_512((settings.SECRET_KEY + password).encode()).hexdigest()
            request.temp_token = temp_token
            log.debug(f'Add request.temp_token="{temp_token[:4]}...{temp_token[-4:]}"')

        return None
