import random
from luhn import generate
from django.conf import settings

__author__ = "Alan Viars"


def random_number(y=10):
    return ''.join(random.choice('123456789') for x in range(y))


def generate_subject_id(prefix=settings.SUBJECT_LUHN_PREFIX, number_1="", number_2=""):
    if not number_1 or len(number_1) != 10:
        number_1 = random_number(10)
    if not number_2 or len(number_2) != 4:
        number_2 = random_number(4)
    number = "%s%s" % (number_1, number_2)
    prefixed_number = "%s%s" % (prefix, number)
    luhn_checksum = generate(prefixed_number)
    return "%s%s" % (number, luhn_checksum)
