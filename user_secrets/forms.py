import logging

from django import forms

from user_secrets.exceptions import DecryptError
from user_secrets.model_fields import EncryptedField
from user_secrets_tests.models import UserSecretsModel


log = logging.getLogger(__name__)


class UserSecretsBaseModelModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance:
            self.decrypt_initial_data()

    def decrypt_initial_data(self):
        """
        Replace decrypted initial data with the decrypted values
        """
        for model_field in self.instance._meta.fields:
            field_name = model_field.name
            if isinstance(model_field, EncryptedField):
                try:
                    decrypted_value = model_field.get_decrypted(self.instance)
                except DecryptError:
                    log.debug('Can not decrypt field %s for initial form data', field_name)
                    continue

                if decrypted_value:
                    self.initial[field_name] = decrypted_value

    class Meta:
        model = UserSecretsModel
        fields = []  # Should be set in child class
