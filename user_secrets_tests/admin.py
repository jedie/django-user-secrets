from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from user_secrets.admin import UserSecretsAdmin
from user_secrets_tests.models import UserSecretsModel


@admin.register(UserSecretsModel)
class ExampleModelAdmin(UserSecretsAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('User Secrets'), {'fields': ('encrypted_secret', 'example_secret')}),  # <<< own fields
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
