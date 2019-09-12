from mnemonic import Mnemonic
from django.utils.crypto import pbkdf2
import binascii
from django.conf import settings


def generate_password_recovery_phrase():
    m = Mnemonic('english')
    mywords = m.generate(256)
    return "%s" % (mywords)


def get_passphrase_salt(salt=settings.PASSPHRASE_SALT):
    """
    Assumes `USER_ID_SALT` is a hex encoded value. Decodes the salt val,
    returning binary data represented by the hexadecimal string.
    :param: salt
    :return: bytes
    """
    return binascii.unhexlify(salt)


def passphrase_hash(passphrase):
    return binascii.hexlify(pbkdf2(passphrase,
                                   get_passphrase_salt(),
                                   settings.PASSPHRASE_ITERATIONS)).decode("ascii")
