from django.contrib import messages
from django.views.generic import TemplateView

from user_secrets.crypto import user_decrypt
from user_secrets.exceptions import DecryptError


class DisplayExampleSecretView(TemplateView):
    """
    Minimal example view to demonstrate how to get a encrypted user secret.
    """
    template_name = 'demo/display_example_secret.html'

    def get_context_data(self, **context):
        user = self.request.user  # get current user
        example_secret = user.example_secret  # the the example field value (encrypted)

        if example_secret is not None:
            # decrypt the example
            try:
                decrypted_value = user_decrypt(user=user, encrypted_data=example_secret)
            except DecryptError:
                messages.error(self.request, "The secret can't be decrypted!")
            else:
                # Just display the decrypted value on the demo web page
                context.update({
                    'decrypted_value': decrypted_value,
                })
        return super().get_context_data(**context)
