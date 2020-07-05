from django.contrib.auth.models import AbstractUser
from django.db import models

from user_secrets.crypto import user_decrypt
from user_secrets.exceptions import NoUserItermediateSecretError
from user_secrets.model_fields import EncryptedField
from user_secrets.models import AbstractUserSecretsModel


class UserSecretsModel(AbstractUserSecretsModel):
    class Meta:
        verbose_name = AbstractUser.Meta.verbose_name
        verbose_name_plural = AbstractUser.Meta.verbose_name_plural


class ExampleModel(models.Model):
    user = models.OneToOneField(
        UserSecretsModel,
        unique=True,
        db_index=True,
        on_delete=models.CASCADE,
    )
    encrypted_password = EncryptedField(
        max_length=256,
        user_field='user',
        verbose_name='Password',
    )

    def decrypt(self, *, user):
        try:
            self.encrypted_password = user_decrypt(user=user, encrypted_data=self.encrypted_password)
        except NoUserItermediateSecretError:
            pass

    def __str__(self):
        return f'ExampleModel entry for user: {self.user}'
