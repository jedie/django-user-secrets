import logging

from django.contrib.auth.models import AbstractUser
from django.db import models

from user_secrets.crypto import encrypt_user_raw_user_token, generate_raw_user_token, get_user_raw_user_token


log = logging.getLogger(__name__)


class UserSecrets(AbstractUser):
    encrypted_secret = models.CharField(
        max_length=256,
        null=True,
        blank=True,
    )

    def set_password(self, raw_password):
        super().set_password(raw_password)
        raw_user_token = None
        if self.encrypted_secret is not None:
            # Existing user changed his password
            log.debug('Save existing secret with new password')
            raw_user_token = get_user_raw_user_token(user=self)

        if not raw_user_token:
            log.debug('New user -> generate new token')
            raw_user_token = generate_raw_user_token()

        self.encrypted_secret = encrypt_user_raw_user_token(
            raw_user_token=raw_user_token,
            raw_password=raw_password
        )

        if self.pk is None:
            # New user created
            self.save()
        else:
            # New password for existing user
            self.save(update_fields=('password', 'encrypted_secret',))
