from django.contrib.auth.hashers import mask_hash
from django.views.generic import TemplateView

from user_secrets.caches import get_user_itermediate_secret


class DemoView(TemplateView):
    template_name = 'demo/index.html'

    def get_context_data(self, **context):
        itermediate_secret = get_user_itermediate_secret(user=self.request.user)
        if itermediate_secret is None:
            itermediate_secret_length = None
            masked_secret = None
        else:
            itermediate_secret_length = len(itermediate_secret)
            masked_secret = mask_hash(hash=itermediate_secret, show=6, char="*")

        context.update({
            'user': self.request.user,
            'has_permission': True,  # enable '{% block usertools %}'
            'masked_secret': masked_secret,
            'itermediate_secret_length': itermediate_secret_length,
        })
        return super().get_context_data(**context)
