from cryptography.fernet import Fernet
from django.contrib.auth import authenticate, get_user_model
from django.test import RequestFactory, TestCase

from user_secrets.crypto import decrypt_user_raw_user_token, get_user_raw_user_token


UserModel = get_user_model()


class SettingsTests(TestCase):
    def setUp(self):
        super().setUp()
        self.test_user = UserModel.objects.create(username='A user')
        self.test_user.set_password('A Passwort')

    def test_encrypted_secret(self):
        user = UserModel.objects.get(pk=self.test_user.pk)
        encrypted_secret = user.encrypted_secret
        assert encrypted_secret is not None
        raw_user_token = decrypt_user_raw_user_token(
            encrypted_secret=encrypted_secret,
            raw_password='A Passwort',
        )
        assert raw_user_token is not None

    def test_authenticate_without_request(self):
        assert self.test_user.check_password('A Passwort') is True
        user = authenticate(username='A user', password='A Passwort')
        assert isinstance(user, UserModel)

        raw_user_token = get_user_raw_user_token(user=user)
        assert raw_user_token is None

    def test_authenticate_with_request(self):
        request = RequestFactory().get('/somewhere')
        user = authenticate(request=request, username='A user', password='A Passwort')
        assert isinstance(request.fernet, Fernet)
