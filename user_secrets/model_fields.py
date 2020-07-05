import logging

from django.contrib.auth import get_user_model
from django.core import checks
from django.db import models

from user_secrets.crypto import user_decrypt, user_encrypt


log = logging.getLogger(__name__)


class EncryptedField(models.CharField):
    def __init__(self, blank=None, null=None, **kwargs):
        # blank and null should be set explicite to True in model definition!
        # see also: self._check_instance()
        self.blank = blank
        self.null = null
        super().__init__(blank=blank, null=null, **kwargs)

    def check(self, **kwargs):
        return [
            *super().check(**kwargs),
            *self._check_instance(**kwargs),
        ]

    def _check_instance(self, **kwargs):
        errors = []

        UserModel = get_user_model()
        own_model = self.model
        if own_model != UserModel:
            errors.append(
                checks.Error(
                    'EncryptedField not used on the user model!',
                    obj=self,
                    id='fields.E201',
                )
            )

        if self.blank is not True or self.null is not True:
            errors.append(
                checks.Error(
                    'EncryptedField must have "blank=True" and "null=True".',
                    obj=self,
                    id='fields.E202',
                )
            )
        return errors

    def get_decrypted(self, instance):
        attribute_name = self.get_attname()
        encrypted_data = getattr(instance, attribute_name)
        if not encrypted_data:
            log.info('%s.%s is empty, ok.', self.model._meta.label, attribute_name)
            return None

        decrypted_data = user_decrypt(user=instance, encrypted_data=encrypted_data)
        return decrypted_data

    def save_form_data(self, instance, data):
        if data is None:
            encrypted_data = None
        else:
            encrypted_data = user_encrypt(
                user=instance,
                data=data
            )
        return super().save_form_data(instance, encrypted_data)
