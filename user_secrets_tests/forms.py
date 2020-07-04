from django import forms

from user_secrets_tests.models import ExampleModel


def set_form_user(*, form, user, field_name='user'):
    user_field = form.base_fields[field_name]
    user_field.disabled = True  # always use initial value for this field
    user_field.initial = user


class ExampleModelForm(forms.ModelForm):
    def set_user(self, *, user):
        set_form_user(form=self, user=user)

    class Meta:
        model = ExampleModel
        fields = ['user', 'encrypted_password']
