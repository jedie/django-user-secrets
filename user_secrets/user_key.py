import logging
import threading

from user_secrets.exceptions import NoUserKeyError


log = logging.getLogger(__name__)
_KEY_STORAGE = threading.local()


def set_user_key(key):
    log.debug('set user key to %s', id(_KEY_STORAGE))
    _KEY_STORAGE.user_key = key


def get_user_key():
    log.debug('get user key from %s', id(_KEY_STORAGE))
    try:
        return _KEY_STORAGE.user_key
    except AttributeError:
        raise NoUserKeyError()


def del_user_key():
    log.debug('delete user key from %s', id(_KEY_STORAGE))
    if hasattr(_KEY_STORAGE, 'user_key'):
        delattr(_KEY_STORAGE, 'user_key')
