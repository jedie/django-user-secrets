import logging

from django.contrib.auth import get_user_model
from django_tools.unittest_utils.unittest_base import BaseTestCase

from user_secrets.caches import delete_user_itermediate_secret, get_user_itermediate_secret
from user_secrets.crypto import user_decrypt
from user_secrets_tests.models import ExampleModel
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

        itermediate_secret1 = get_user_itermediate_secret(user=test_user)

        response = self.client.get('/admin/')
        self.assertRedirects(response, expected_url='/admin/login/?next=%2Fadmin%2F')

        delete_user_itermediate_secret(user=test_user)
        response = self.client.post(
            path='/admin/login/',
            data={
                'username': 'a user',
                'password': 'A Password!'
            }
        )
        self.assertRedirects(response, expected_url='/')

        itermediate_secret2 = get_user_itermediate_secret(user=test_user)
        assert itermediate_secret2 == itermediate_secret1

        response = self.client.get('/admin/user_secrets_tests/examplemodel/add/')
        self.assertResponse(
            response=response,
            must_contain=(
                '<title>Add example model | Django site admin</title>',
                '<label class="required" for="id_user">User:</label>',
                f'<option value="{test_user.pk}" selected>a user</option>',
                '<label class="required" for="id_encrypted_password">Password:</label>',
            ),
            status_code=200,
            template_name='admin/change_form.html',
            messages=None,
        )

        assert ExampleModel.objects.count() == 0

        response = self.client.post(
            path='/admin/user_secrets_tests/examplemodel/add/',
            data={'encrypted_password': 'Not a Secret?!?'}
        )
        self.assertRedirects(response, expected_url='/admin/user_secrets_tests/examplemodel/')
        assert ExampleModel.objects.count() == 1
        entry = ExampleModel.objects.first()

        the_secret = user_decrypt(user=test_user, encrypted_data=entry.encrypted_password)
        assert the_secret == 'Not a Secret?!?'

        response = self.client.get(f'/admin/user_secrets_tests/examplemodel/{entry.pk}/change/')
        self.assertResponse(
            response=response,
            must_contain=(
                '<title>Change example model | Django site admin</title>',
                '<label class="required" for="id_user">User:</label>',
                f'<option value="{test_user.pk}" selected>a user</option>',
                '<label class="required" for="id_encrypted_password">Password:</label>',
            ),
            must_not_contain=(
                'Not a Secret?!?',  # the admin doesn't display the encrypted data
            ),
            status_code=200,
            template_name='admin/change_form.html',
            messages=None,
        )
