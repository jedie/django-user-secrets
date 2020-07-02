import logging

from django.contrib.auth.models import AbstractUser
from django.db import models

from user_secrets.caches import set_user_itermediate_secret
from user_secrets.crypto import generate_encrypted_secret


log = logging.getLogger(__name__)


class UserSecrets(AbstractUser):
    encrypted_secret = models.CharField(
        max_length=256,
        null=True,
        blank=True,
    )

    def set_password(self, raw_password):
        super().set_password(raw_password)

        if self.encrypted_secret is not None:
            log.error('Use password change: All stored encrypted data lost!')
            # TODO: Implement a own password change with re-encrypt existing data!
        else:
            log.info('Set generate encrypted secret for new user')

        itermediate_secret, self.encrypted_secret = generate_encrypted_secret(
            raw_password=raw_password
        )
        set_user_itermediate_secret(user=self, itermediate_secret=itermediate_secret)

        if self.pk is None:
            # New user created
            self.save()
        else:
            # New password for existing user
            self.save(update_fields=('password', 'encrypted_secret',))

        log.debug(f'New encrypted secret saved for user: {self.pk}')
