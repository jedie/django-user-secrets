from django.contrib import admin, messages

from user_secrets.caches import get_user_itermediate_secret
from user_secrets_tests.forms import set_form_user
from user_secrets_tests.models import ExampleModel


@admin.register(ExampleModel)
class ExampleModelAdmin(admin.ModelAdmin):
    list_display = ('user', 'encrypted_password')
    list_display_links = ('encrypted_password', 'user')

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj=obj, **kwargs)
        set_form_user(form=form, user=request.user)
        return form

    def _changeform_view(self, request, object_id, form_url, extra_context):
        itermediate_secret = get_user_itermediate_secret(user=request.user)
        if itermediate_secret is None:
            messages.warning(request, 'Raw user itermediate secret not set')

        return super()._changeform_view(request, object_id, form_url, extra_context)
