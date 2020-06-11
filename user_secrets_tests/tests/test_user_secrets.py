from django.contrib.auth import authenticate, get_user_model
from django.test import TestCase


UserModel = get_user_model()


class SettingsTests(TestCase):
    def setUp(self):
        super().setUp()
        self.test_user = UserModel.objects.create(
            username='A user',
        )
        self.test_user.set_password('A Passwort')

    def test_authenticate_without_request(self):
        assert self.test_user.check_password('A Passwort') is True
        user = authenticate(username='A user', password='A Passwort')
        assert isinstance(user, UserModel)
