from user_secrets.forms import UserSecretsBaseModelModelForm
from user_secrets_tests.models import UserSecretsModel


class ExampleModelForm(UserSecretsBaseModelModelForm):
    class Meta:
        model = UserSecretsModel
        fields = ['example_secret']
