import logging

from django.conf import settings
from django.contrib.auth.views import LogoutView

from user_secrets.caches import get_user_itermediate_secret


log = logging.getLogger(__name__)


class UserSecretsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        assert hasattr(request, 'user'), (
            'UserSecretsMiddleware must be insert after AuthenticationMiddleware'
            " Edit your MIDDLEWARE%s setting!"
        ) % ("_CLASSES" if settings.MIDDLEWARE is None else "")

        user = request.user
        if user.is_authenticated:
            itermediate_secret = get_user_itermediate_secret(user=request.user)
            if itermediate_secret is None:
                if user.encrypted_secret is None:
                    log.debug('user.encrypted_secret not set for user: %s', user.pk)
                else:
                    log.info('itermediate_secret not in cache: Logout user: %s', user.pk)
                    # A encrypted_secret is stored, but itermediate_secret not in cache
                    # Log the user out and redirect to login page:
                    return LogoutView.as_view(next_page=request.path)(request)

        response = self.get_response(request)

        return response
