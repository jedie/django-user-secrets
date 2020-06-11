from django.conf import settings
from django.core.management import call_command
from django.test import SimpleTestCase
from django_tools.unittest_utils.stdout_redirect import StdoutStderrBuffer


class SettingsTests(SimpleTestCase):

    def test_settings_module(self):
        assert settings.SETTINGS_MODULE == 'user_secrets_tests.settings'

    def test_diffsettings(self):
        """
        Check some settings
        """
        with StdoutStderrBuffer() as buff:
            call_command('diffsettings')
        output = buff.get_output()
        print(output)
        self.assertIn('user_secrets_tests.settings', output)  # SETTINGS_MODULE


class ManageCheckTests(SimpleTestCase):

    def test_django_check(self):
        """
        call './manage.py check' directly via 'call_command'
        """
        with StdoutStderrBuffer() as buff:
            call_command('check')
        output = buff.get_output()
        self.assertIn('System check identified no issues (0 silenced).', output)
