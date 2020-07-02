import logging
import unittest

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from user_secrets.caches import get_user_itermediate_secret
from user_secrets.crypto import Cryptor, secret2fernet_key, user_decrypt, user_encrypt
from user_secrets.exceptions import NoUserKeyError
from user_secrets.user_key import del_user_key, get_user_key, _KEY_STORAGE, set_user_key


UserModel = get_user_model()


class ClearKeyStorageMixin:
    def setUp(self) -> None:
        super().setUp()
        del_user_key()

    def tearDown(self) -> None:
        super().tearDown()
        del_user_key()


class CryptorTestCase(ClearKeyStorageMixin, unittest.TestCase):

    def test_ascii(self):
        c = Cryptor(secret='password')
        encrypted_data = c.encrypt(data='test')
        assert isinstance(encrypted_data, str)
        assert c.decrypt(encrypted_data=encrypted_data) == 'test'
        assert Cryptor(secret='password').decrypt(encrypted_data=encrypted_data) == 'test'

        fernet_key = secret2fernet_key(secret='password')
        assert Cryptor(fernet_key=fernet_key).decrypt(encrypted_data=encrypted_data) == 'test'

    def test_non_ascii(self):
        c = Cryptor(secret='Pass äöüß !')
        encrypted_data = c.encrypt(data='Test äöüß !')
        assert isinstance(encrypted_data, str)
        assert c.decrypt(encrypted_data=encrypted_data) == 'Test äöüß !'
        assert Cryptor(secret='Pass äöüß !').decrypt(encrypted_data=encrypted_data) == 'Test äöüß !'

        fernet_key = secret2fernet_key(secret='Pass äöüß !')
        assert Cryptor(fernet_key=fernet_key).decrypt(encrypted_data=encrypted_data) == 'Test äöüß !'

    def test_user_key(self):
        with self.assertRaises(NoUserKeyError):
            get_user_key()

        set_user_key(key='foobar')
        assert get_user_key() == 'foobar'

        del_user_key()
        del_user_key()  # second call should be made no error

        with self.assertRaises(NoUserKeyError):
            get_user_key()


class CryptoTestCase(ClearKeyStorageMixin, TestCase):

    def test(self):
        assert UserModel.objects.count() == 0

        # create new user
        test_user = UserModel.objects.create(username='a user')
        with self.assertLogs('user_secrets', level=logging.DEBUG) as logs:
            test_user.set_password('A Password!')
        assert logs.output == [
            'INFO:user_secrets.models:Set generate encrypted secret for new user',
            f'DEBUG:user_secrets.caches:Save itermediate_secret to cache for user: {test_user.pk}',
            f'DEBUG:user_secrets.models:New encrypted secret saved for user: {test_user.pk}',
        ]

        # users "encrypted_secret" saved?
        test_user = UserModel.objects.get(pk=test_user.pk)
        assert test_user.encrypted_secret

        # We should decrypt the secret with the password:
        secret = Cryptor(secret='A Password!').decrypt(encrypted_data=test_user.encrypted_secret)
        assert secret is not None

        # Login the user:
        request = RequestFactory().get('/somewhere')
        with self.assertLogs('user_secrets', level=logging.DEBUG) as logs:
            self.client.login(request=request, username='a user', password='A Password!')

        key_storage_id = id(_KEY_STORAGE)
        assert logs.output == [
            'DEBUG:user_secrets.auth_backend:create fernet key from password',
            f'DEBUG:user_secrets.user_key:set user key to {key_storage_id}',
            'DEBUG:user_secrets.signals:User logged in',
            f'DEBUG:user_secrets.user_key:get user key from {key_storage_id}',
            f'DEBUG:user_secrets.caches:Save itermediate_secret to cache for user: {test_user.pk}',
        ]

        # decrypted secret is in cache?
        token = get_user_itermediate_secret(user=test_user)

        # It's the same?
        assert token == secret

        # Use the low level user encrypt/decrypt functions:
        test_data = 'Test äöüß !'
        encrypted_data = user_encrypt(user=test_user, data=test_data)
        assert encrypted_data != test_data
        data2 = user_decrypt(user=test_user, encrypted_data=encrypted_data)
        assert data2 == test_data
