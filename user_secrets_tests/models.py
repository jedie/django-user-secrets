from user_secrets.crypto import user_decrypt
from user_secrets.exceptions import NoUserItermediateSecretError
from user_secrets.model_fields import EncryptedField
from user_secrets.models import AbstractUserSecretsModel


class UserSecretsModel(AbstractUserSecretsModel):
    example_secret = EncryptedField(
        max_length=256,
        blank=True,
        null=True,
        verbose_name='Example Secret',
        help_text=(
            'Here you can test the encryption: Just enter anything,'
            ' it will be stored encrypted and only you can decrypt it!'
        )
    )

    def decrypted_example_secret(self):
        try:
            return user_decrypt(user=self, encrypted_data=self.example_secret)
        except NoUserItermediateSecretError:
            pass
