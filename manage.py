#!/usr/bin/env python
import os
import sys
from vmi.ssmenv import EC2ParameterStore
# import dotenv

if __name__ == '__main__':
    # dotenv.read_dotenv()
    try:
        parameter_store = EC2ParameterStore(region_name="us-east-1")
        # Automate env (dev)
        django_parameters = parameter_store.get_parameters_by_path(
            '/dev/vmi/',
            strip_path=True)
        EC2ParameterStore.set_env(django_parameters)
    except Exception:
        pass

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vmi.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)
