class CryptoError(Exception):
    pass


class DecryptError(CryptoError):
    pass


class NoUserItermediateSecretError(CryptoError):
    pass


class NoUserKeyError(CryptoError):
    pass
