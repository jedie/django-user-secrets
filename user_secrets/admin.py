from django.contrib import messages
from django.contrib.auth.admin import UserAdmin as OriginUserAdmin
from django.utils.translation import gettext_lazy as _

from user_secrets.caches import get_user_itermediate_secret


class UserSecretsAdmin(OriginUserAdmin):
    fieldsets = (  # should be expand with encrypted field in child class
        (None, {'fields': ('username', 'password')}),
        (_('User Secrets'), {'fields': ('encrypted_secret')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    readonly_fields = ('encrypted_secret',)

    def _changeform_view(self, request, object_id, form_url, extra_context):
        itermediate_secret = get_user_itermediate_secret(user=request.user)
        if itermediate_secret is None:
            messages.warning(request, 'Raw user itermediate secret not set')

        return super()._changeform_view(request, object_id, form_url, extra_context)
