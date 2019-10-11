import random
from luhn import generate
from django.conf import settings

__author__ = "Alan Viars"


def random_number(y=10):
    return ''.join(random.choice('1234567890') for x in range(y))


def generate_subject_id(prefix=settings.SUBJECT_LUHN_PREFIX, starts_with="1",  number_str_include=""):
    # Generate a subject according to https://github.com/TransparentHealth/uhi
    # Supply up to 10 numbers you want in the resulting number.
    max_allowed_pickable_nums = 10
    size_of_between_number = 13
    if not number_str_include.isnumeric():
        number_str_include = ""
    # numbers can be any length from 0 - 13
    len_numbers = len(number_str_include)
    if len_numbers > max_allowed_pickable_nums:
        number_str_include = number_str_include[0:max_allowed_pickable_nums]
    remaining = size_of_between_number - len(number_str_include)
    padding = random_number(remaining)
    number = "%s%s%s" % (starts_with, number_str_include, padding)
    prefixed_number = "%s%s" % (prefix, number)
    luhn_checksum = generate(prefixed_number)
    return "%s%s" % (number, luhn_checksum)
