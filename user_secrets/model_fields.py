from django.contrib.auth import get_user_model
from django.core import checks
from django.db import models

from user_secrets.crypto import user_encrypt


UserModel = get_user_model()


class EncryptedField(models.CharField):
    def __init__(self, user_field=None, **kwargs):
        self.user_field = user_field
        super().__init__(**kwargs)

    def check(self, **kwargs):
        return [
            *super().check(**kwargs),
            *self._check_user_field(),
        ]

    def _get_user_field(self):
        meta_field = self.model._meta.get_field(self.user_field)
        return meta_field

    def _check_user_field(self):
        errors = []
        if not self.user_field:
            errors.append(
                checks.Error(
                    f"'user_field' is not defined for {self.__class__.__name__!r}.",
                    obj=self,
                    id='fields.E201',
                )
            )
        else:
            meta_field = self._get_user_field()
            if not isinstance(meta_field, models.OneToOneField):
                errors.append(
                    checks.Error(
                        f'Meta field {meta_field} for {self.__class__.__name__!r}'
                        f' is not a OneToOneField',
                        obj=self,
                        id='fields.E201',
                    )
                )
            related_model = meta_field.related_model
            if related_model != UserModel:
                errors.append(
                    checks.Error(
                        f'Meta field {meta_field}'
                        f' must point to User model: {UserModel.__name__!r}!'
                        f' (It points currently to: {related_model.__name__!r}',
                        obj=self,
                        id='fields.E201',
                    )
                )

        return errors

    def save_form_data(self, instance, data):
        encrypted_data = user_encrypt(
            user=instance.user,
            data=data
        )
        return super().save_form_data(instance, encrypted_data)
