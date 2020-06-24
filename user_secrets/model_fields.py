import time

from django.contrib.auth import get_user_model
from django.core import checks
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from user_secrets.crypto import encrypt


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
        encrypted_data = encrypt(
            user=instance.user,
            data=data
        )
        return super().save_form_data(instance, encrypted_data)

        raw_user_token = get_user_raw_user_token(user=user)

        print(instance)
        print(instance.user)
        print(instance.encrypted_password)
        print(self.attname)
        encrypted_password = getattr(instance, self.attname)
        print(encrypted_password)
        raise

    # def from_db_value(self, value, expression, connection):
    #     if value is None:
    #         return value
    #     return parse_hand(value)
    #
    # def to_python(self, value):
    #     if isinstance(value, Hand):
    #         return value
    #
    #     if value is None:
    #         return value
    #
    #     return parse_hand(value)
