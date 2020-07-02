import logging

from django.core.cache import caches


log = logging.getLogger(__name__)

CACHE_PATTERN = 'itermediate_secret_{user_pk}'


def get_cache_key(user):
    key = CACHE_PATTERN.format(user_pk=user.pk)
    return key


def set_user_itermediate_secret(*, user, itermediate_secret):
    log.debug(f'Save itermediate_secret to cache for user: {user.pk}')
    cache = caches['user_secrets']
    cache_key = get_cache_key(user=user)
    cache.set(cache_key, itermediate_secret)


def get_user_itermediate_secret(*, user):
    log.debug(f'Get itermediate_secret from cache for user: {user.pk}')
    cache = caches['user_secrets']
    cache_key = get_cache_key(user=user)
    return cache.get(cache_key)


def delete_user_itermediate_secret(*, user):
    log.debug(f'Delete itermediate_secret from cache for user: {user.pk}')
    cache = caches['user_secrets']
    cache_key = get_cache_key(user=user)
    cache.delete(cache_key)
