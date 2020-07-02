from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as OriginUserAdmin
from django.utils.translation import gettext_lazy as _

from user_secrets.models import UserSecrets


@admin.register(UserSecrets)
class UserAdmin(OriginUserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password', 'encrypted_secret')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    readonly_fields = ('encrypted_secret',)
