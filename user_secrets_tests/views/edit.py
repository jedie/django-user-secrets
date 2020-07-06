import logging

from django.contrib import messages
from django.contrib.auth.hashers import mask_hash
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView

from user_secrets.caches import get_user_itermediate_secret
from user_secrets.crypto import user_get_datetime
from user_secrets_tests.forms import ExampleModelForm
from user_secrets_tests.models import UserSecretsModel


log = logging.getLogger(__name__)


class EditExampleSecretView(TemplateView):
    template_name = 'demo/edit_example_secret.html'

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
            encrypted_data=self.request.user.example_secret
        )

        context.update({
            'user': user,
            'has_permission': True,  # enable '{% block usertools %}'
            'opts': UserSecretsModel._meta,
            'example_secret': self.request.user.example_secret,
            'token_dt': token_dt,
            'masked_secret': masked_secret,
            'itermediate_secret_length': itermediate_secret_length,
        })
        return super().get_context_data(**context)

    def get(self, request, *args, **kwargs):
        itermediate_secret = get_user_itermediate_secret(user=request.user)
        assert itermediate_secret is not None  # UserSecretsMiddleware should prevent this

        example_secret = request.user.example_secret  # display encrypted example secret
        form = ExampleModelForm(instance=request.user)
        context = {
            'form': form,
            'example_secret': example_secret,
            'instance': request.user,
        }
        return self.render_to_response(context)

    def post(self, request):
        form = ExampleModelForm(instance=request.user, data=self.request.POST)
        if form.is_valid():
            if form.has_changed():
                log.info('Change fields: %s', ', '.join(form.changed_data))
                form.save()

            messages.info(self.request, 'Secret saved encrypted, ok.')
            return HttpResponseRedirect('/')

        return self.render_to_response(context={'form': form})

    def render_to_response(self, context, **response_kwargs):
        context = self.get_context_data(**context)
        return super().render_to_response(context, **response_kwargs)
