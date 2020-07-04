import logging

from django.contrib import messages
from django.contrib.auth.hashers import mask_hash
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView

from user_secrets.caches import get_user_itermediate_secret
from user_secrets.crypto import user_get_datetime
from user_secrets_tests.forms import ExampleModelForm
from user_secrets_tests.models import ExampleModel


log = logging.getLogger(__name__)


class DemoView(TemplateView):
    template_name = 'demo/index.html'

    def get_instance(self):
        qs = ExampleModel.objects.filter(user=self.request.user)
        if qs.exists():
            example_instance = qs.get()
            self.encrypted_password = example_instance.encrypted_password
            example_instance.decrypt(user=self.request.user)
        else:
            example_instance = None
            self.encrypted_password = None

        return example_instance

    def get_context_data(self, **context):
        user = self.request.user

        itermediate_secret = get_user_itermediate_secret(user=self.request.user)
        if itermediate_secret is None:
            itermediate_secret_length = None
            masked_secret = None
        else:
            itermediate_secret_length = len(itermediate_secret)
            masked_secret = mask_hash(hash=itermediate_secret, show=6, char="*")

        token_dt = user_get_datetime(
            user=user,
            encrypted_data=self.encrypted_password
        )
        context.update({
            'user': user,
            'has_permission': True,  # enable '{% block usertools %}'
            'opts': ExampleModel._meta,
            'encrypted_password': self.encrypted_password,
            'token_dt': token_dt,
            'masked_secret': masked_secret,
            'itermediate_secret_length': itermediate_secret_length,
        })
        return super().get_context_data(**context)

    def get_form(self, request, obj=None, data=None):
        form = ExampleModelForm(instance=obj, data=data)
        form.set_user(user=request.user)
        return form

    def get(self, request, *args, **kwargs):
        itermediate_secret = get_user_itermediate_secret(user=request.user)
        assert itermediate_secret is not None  # UserSecretsMiddleware should prevent this

        instance = self.get_instance()
        form = self.get_form(request, obj=instance)
        context = {
            'form': form,
            'instance': instance,
        }
        return self.render_to_response(context)

    def post(self, request):
        instance = self.get_instance()
        form = self.get_form(request, obj=instance, data=self.request.POST)
        if form.is_valid():
            if form.has_changed():
                log.info('Change fields: %s', ', '.join(form.changed_data))
                form.save()

            messages.info(self.request, 'Form saved, ok.')
            return HttpResponseRedirect('/')

        return self.render_to_response(context={'form': form})

    def render_to_response(self, context, **response_kwargs):
        context = self.get_context_data(**context)
        return super().render_to_response(context, **response_kwargs)
