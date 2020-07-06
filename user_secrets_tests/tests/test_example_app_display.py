import logging

from django.contrib.auth import get_user_model
from django_tools.unittest_utils.unittest_base import BaseTestCase

from user_secrets.caches import delete_user_itermediate_secret, get_user_itermediate_secret
from user_secrets.crypto import user_encrypt
from user_secrets_tests.tests.test_crypto import ClearKeyStorageMixin


UserModel = get_user_model()


class ExampleAppDisplayTestCase(ClearKeyStorageMixin, BaseTestCase):
    """
    Tests for: user_secrets_tests.views.display.DisplayExampleSecretView
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

        response = self.client.get('/demo/')
        self.assertRedirects(response, expected_url='/admin/login/?next=%2Fdemo%2F')

        delete_user_itermediate_secret(user=test_user)
        response = self.client.post(
            path='/admin/login/?next=%2Fdemo%2F',
            data={
                'username': 'a user',
                'password': 'A Password!'
            }
        )
        self.assertRedirects(response, expected_url='/demo/')

        itermediate_secret2 = get_user_itermediate_secret(user=test_user)
        assert itermediate_secret2 == itermediate_secret1

        response = self.client.get('/demo/')
        self.assertResponse(
            response=response,
            must_contain=(
                '<title>Django-User-Secrets DEMO</title>',
                "<p>No example secret saved, yet or it can's decrypted.</p>",
            ),
            must_not_contain=(
                'DecryptError',
            ),
            status_code=200,
            template_name='demo/display_example_secret.html',
            messages=[],
        )

        # Test DecryptError by save not encrypted data:

        test_user.example_secret = 'This is is not encrypted -> DecryptError will raise'
        test_user.save()

        response = self.client.get('/demo/')
        self.assertResponse(
            response=response,
            must_contain=(
                '<title>Django-User-Secrets DEMO</title>',
                "<p>No example secret saved, yet or it can's decrypted.</p>",
            ),
            must_not_contain=(
                'This is is not encrypted -> DecryptError will raise',
            ),
            status_code=200,
            template_name='demo/display_example_secret.html',
            messages=["The secret can't be decrypted!"],
        )

        test_user.example_secret = user_encrypt(
            user=test_user,
            data='This is the example secret!'
        )
        test_user.save()

        response = self.client.get('/demo/')
        self.assertResponse(
            response=response,
            must_contain=(
                '<title>Django-User-Secrets DEMO</title>',
                '<pre>This is the example secret!</pre>',
            ),
            must_not_contain=(
                'No example secret saved',
                'DecryptError',
            ),
            status_code=200,
            template_name='demo/display_example_secret.html',
            messages=[],
        )
