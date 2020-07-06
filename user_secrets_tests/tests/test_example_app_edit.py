import logging

from django.contrib.auth import get_user_model
from django_tools.unittest_utils.unittest_base import BaseTestCase

from user_secrets.caches import delete_user_itermediate_secret, get_user_itermediate_secret
from user_secrets_tests.tests.test_crypto import ClearKeyStorageMixin


UserModel = get_user_model()


class ExampleAppEditTestCase(ClearKeyStorageMixin, BaseTestCase):
    """
    Tests for: user_secrets_tests.views.edit.EditExampleSecretView
    """

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

        response = self.client.get('/')
        self.assertRedirects(response, expected_url='/admin/login/?next=%2F')

        delete_user_itermediate_secret(user=test_user)
        response = self.client.post(
            path='/admin/login/?next=%2F',
            data={
                'username': 'a user',
                'password': 'A Password!'
            }
        )
        self.assertRedirects(response, expected_url='/')

        itermediate_secret2 = get_user_itermediate_secret(user=test_user)
        assert itermediate_secret2 == itermediate_secret1

        response = self.client.get('/')
        self.assertResponse(
            response=response,
            must_contain=(
                '<title>Django-User-Secrets DEMO</title>',
                'Please save something:',

                '<input type="text" name="example_secret" maxlength="256" id="id_example_secret">',

                '<p>example secret: (nothing saved, yet.)</p>',
            ),
            status_code=200,
            template_name='demo/edit_example_secret.html',
            messages=None,
        )

        response = self.client.post(
            path='/',
            data={'example_secret': 'Not a Secret?!?'}
        )
        self.assertRedirects(response, expected_url='/', fetch_redirect_response=False)
        self.assertMessages(response, messages=['Secret saved encrypted, ok.'])

        test_user = UserModel.objects.get(pk=test_user.pk)
        assert test_user.encrypted_secret is not None
        assert test_user.example_secret is not None

        assert test_user.decrypted_example_secret() == 'Not a Secret?!?'

        response = self.client.get('/')
        self.assertResponse(
            response=response,
            must_contain=(
                '<title>Django-User-Secrets DEMO</title>',

                '<input type="text" name="example_secret" value="Not a Secret?!?"'
                ' maxlength="256" id="id_example_secret">',

                f'/admin/user_secrets_tests/usersecretsmodel/{test_user.pk}/change/'
            ),
            must_not_contain=(
                'Please save something',
                'nothing saved, yet.',
            ),
            status_code=200,
            template_name='demo/edit_example_secret.html',
            messages=['Secret saved encrypted, ok.'],
        )
