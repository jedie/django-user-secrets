from django.contrib.auth import get_user_model
from django.db import models

from user_secrets.model_fields import EncryptedField


UserModel = get_user_model()


class ExampleModel(models.Model):
    user = models.OneToOneField(
        UserModel,
        on_delete=models.CASCADE
    )
    encrypted_password = EncryptedField(
        max_length=256,
        user_field='user'
    )
