import logging

from django.contrib.auth.models import AbstractUser
from django.db import models

from user_secrets.caches import get_user_itermediate_secret, set_user_itermediate_secret
from user_secrets.crypto import encrypt_itermediate_secret, generate_encrypted_secret


log = logging.getLogger(__name__)


class UserSecrets(AbstractUser):
    encrypted_secret = models.CharField(
        max_length=256,
        null=True,
        blank=True,
    )

    def set_password(self, raw_password):
        log.debug('Set password for user: %s', self.pk)
        super().set_password(raw_password)

        if self.encrypted_secret is not None:
            itermediate_secret = get_user_itermediate_secret(user=self)
            if itermediate_secret:
                log.info('Password change: Update encrypted secret for user: %s', self.pk)
                self.encrypted_secret = encrypt_itermediate_secret(
                    itermediate_secret=itermediate_secret,
                    raw_password=raw_password
                )
            else:
                log.error('encrypted_secret set but itermediate_secret missing!')
                return
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

        log.debug('New encrypted secret saved for user: %s', self.pk)
