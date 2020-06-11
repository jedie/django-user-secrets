import logging

from django.contrib.auth import get_user_model, user_logged_in, user_logged_out, user_login_failed
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver


log = logging.getLogger(__name__)
UserModel = get_user_model()


@receiver(user_logged_in)
def user_logged_in_callback(*, sender, request, user, **kwargs):
    log.debug('User logged in')
    print(sender, request, user)


@receiver(user_logged_out)
def user_logged_in_callback(*, sender, request, user, **kwargs):
    log.debug('User logged out')
    print(sender, request, user)


@receiver(user_login_failed)
def user_login_failed_callback(*, sender, credentials, request, **kwargs):
    log.debug('User login failed -> set request.temp_token = None')
    request.temp_token = None
    print(sender, credentials, request)


@receiver(post_save, sender=UserModel)
def user_model_post_save_callback(sender, instance, created, **kwargs):
    print("user_model_post_save_callback", sender, instance, created)


@receiver(post_delete, sender=UserModel)
def user_model_post_delete_callback(sender, **kwargs):
    print("user_model_post_delete_callback", sender, kwargs)
