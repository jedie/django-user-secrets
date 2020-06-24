from django.apps import AppConfig


class UserSecretsConfig(AppConfig):
    name = 'user_secrets'

    def ready(self):
        import user_secrets.checks  # noqa - activate own system checks
        import user_secrets.signals  # noqa - register signal handlers
