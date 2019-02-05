from Crypto.PublicKey import RSA
from jwkest.jwk import RSAKey
from .settings import oidc_settings


def get_key_storage():
    return oidc_settings.OIDC_KEY_STORAGE()


class FileKeyStore(object):
    _private_key_file = "private.pem"
    _public_key_file = "public.pem"

    def store_private(self, key_string):
        file_out = open(self._private_key_file, "wb")
        file_out.write(key_string)

    def store_public(self, key_string):
        file_out = open(self._public_key_file, "wb")
        file_out.write(key_string)

    @property
    def private(self):
        return open(self._private_key_file).read()

    @property
    def public(self):
        return open(self._public_key_file).read()


class RSA256Keys(object):

    # TODO regenerate keys
    def generate_keys(self):
        key = RSA.generate(2048)
        private_key = key.export_key()
        get_key_storage().store_private(private_key)

        public_key = key.publickey().export_key()
        get_key_storage().store_public(public_key)

    def get_public_key(self):
        try:
            return get_key_storage().public
        except IOError:
            self.generate_keys()
            return get_key_storage().public

    def get_public_jwk(self):
        try:
            _rsakey = get_key_storage().public
        except FileNotFoundError:
            self.generate_keys()
            _rsakey = get_key_storage().public
        _rsakey = RSA.import_key(_rsakey)
        _rsajwk = RSAKey(use="sig", alg="RS256", key=_rsakey)
        _rsajwk.add_kid()
        return _rsajwk.serialize()

    def get_private_key(self):
        try:
            return get_key_storage().private
        except FileNotFoundError:
            self.generate_keys()
            return get_key_storage().private
