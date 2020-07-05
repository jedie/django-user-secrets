import logging

from django.contrib.auth import get_user_model
from django_tools.unittest_utils.unittest_base import BaseTestCase

from user_secrets.caches import delete_user_itermediate_secret, get_user_itermediate_secret
from user_secrets_tests.tests.test_crypto import ClearKeyStorageMixin


UserModel = get_user_model()


class AdminTestCase(ClearKeyStorageMixin, BaseTestCase):
    def test(self):
        test_user = UserModel.objects.create(username='a user', is_staff=True, is_superuser=True)
        with self.assertLogs('user_secrets', level=logging.DEBUG) as logs:
            test_user.set_password('A Password!')

        assert logs.output == [
            f'DEBUG:user_secrets.models:Set password for user: {test_user.pk}',
            'INFO:user_secrets.models:Set generate encrypted secret for new user',
            f'DEBUG:user_secrets.caches:Save itermediate secret to cache for user: {test_user.pk}',
            f'DEBUG:user_secrets.models:New encrypted secret saved for user: {test_user.pk}',
        ]

        test_user = UserModel.objects.get(pk=test_user.pk)
        assert test_user.encrypted_secret is not None
        assert test_user.example_secret is None

        itermediate_secret1 = get_user_itermediate_secret(user=test_user)

        response = self.client.get('/admin/')
        self.assertRedirects(response, expected_url='/admin/login/?next=%2Fadmin%2F')

        delete_user_itermediate_secret(user=test_user)
        response = self.client.post(
            path='/admin/login/?next=%2Fadmin%2F',
            data={
                'username': 'a user',
                'password': 'A Password!'
            }
        )
        self.assertRedirects(response, expected_url='/admin/')

        itermediate_secret2 = get_user_itermediate_secret(user=test_user)
        assert itermediate_secret2 == itermediate_secret1

        response = self.client.get(
            f'/admin/user_secrets_tests/usersecretsmodel/{test_user.pk}/change/'
        )
        self.assertResponse(
            response=response,
            must_contain=(
                '<title>Change user | Django site admin</title>',

                ' value="a user"',  # <input name="username"...

                '<label>Encrypted secret:</label>',
                f'<div class="readonly">{test_user.encrypted_secret}</div>',

                # Empty, yet:
                '<input type="text" name="example_secret" class="vTextField"'
                ' maxlength="256" id="id_example_secret">'
            ),
            must_not_contain=(
                'Not a Secret?!?',  # the admin doesn't display the encrypted data
            ),
            status_code=200,
            template_name='admin/change_form.html',
            messages=None,
        )

        response = self.client.post(
            path=f'/admin/user_secrets_tests/usersecretsmodel/{test_user.pk}/change/',
            data={
                'username': 'NewUsername',
                'example_secret': 'A Test Secret!',
                'first_name': '',
                'last_name': '',
                'email': '',
                'is_active': 'on',
                'is_staff': 'on',
                'is_superuser': 'on',
                'last_login_0': '2020-07-06',
                'last_login_1': '07:52:06',
                'date_joined_0': '2020-07-06',
                'date_joined_1': '07:36:20',
                'initial-date_joined_0': '2020-07-06',
                'initial-date_joined_1': '07:36:20',
                '_save': 'Save',
            },
        )
        self.assertRedirects(response, expected_url='/admin/user_secrets_tests/usersecretsmodel/')

        test_user = UserModel.objects.get(pk=test_user.pk)
        assert test_user.encrypted_secret is not None
        assert test_user.example_secret is not None

        assert test_user.decrypted_example_secret() == 'A Test Secret!'
