from django.contrib.auth import get_user_model
from django.db import models

from user_secrets.crypto import user_decrypt
from user_secrets.exceptions import NoUserItermediateSecretError
from user_secrets.model_fields import EncryptedField


UserModel = get_user_model()


class ExampleModel(models.Model):
    user = models.OneToOneField(
        UserModel,
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
