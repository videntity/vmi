#!/usr/bin/env python
# import logging
import os
import sys
import dotenv


if __name__ == '__main__':
    # (in dev)
    # logging.basicConfig(
    #     level=DEBUG and 10 or 20,
    #     format="{asctime} {levelname} {name}:{lineno} | {message}",
    #     style="{",
    # )

    dotenv.load_dotenv()
    ENVIRONMENT_VARIABLE_STRATEGY = ".ENV"
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vmi.settings')
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
