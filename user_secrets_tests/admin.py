from django.contrib import admin, messages

from user_secrets.crypto import get_user_raw_user_token
from user_secrets_tests.models import ExampleModel


@admin.register(ExampleModel)
class ExampleModelAdmin(admin.ModelAdmin):
    def _changeform_view(self, request, object_id, form_url, extra_context):
        raw_user_token = get_user_raw_user_token(user=request.user)
        if raw_user_token is None:
            messages.warning(request, 'Raw user token not set')
            
        return super()._changeform_view(request, object_id, form_url, extra_context)


