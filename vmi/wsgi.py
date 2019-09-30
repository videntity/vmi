"""
WSGI config for smh_app project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/howto/deployment/wsgi/
"""

import os
import dotenv
from getenv import env
from django.core.wsgi import get_wsgi_application
from .ssmenv import EC2ParameterStore

AWS_DEFAULT_REGION = env('AWS_DEFAULT_REGION', 'us-east-1')
VPC_ENV = env('VPC_ENV', 'dev')
VPC_APP_NAME = env('VPC_APP_NAME', 'vmi')
PARAMETER_STORE_PATH = "/%s/%s/" % (VPC_ENV, VPC_APP_NAME)


try:
    # Defaulting to .env
    # Get this from .env file from your local development environment or
    # Ansible,

    dotenv.load_dotenv()
    ENVIRONMENT_VARIABLE_STRATEGY = '.ENV'
    EC2PARAMSTORE_4_ENVIRONMENT_VARIABLES = env('EC2PARAMSTORE_4_ENVIRONMENT_VARIABLES',
                                                'EC2_PARAMSTORE')
    # Get via EC2 Parameter store
    if EC2PARAMSTORE_4_ENVIRONMENT_VARIABLES == "EC2_PARAMSTORE":
        parameter_store = EC2ParameterStore(region_name=AWS_DEFAULT_REGION)
        django_parameters = parameter_store.get_parameters_by_path(
            PARAMETER_STORE_PATH, strip_path=True
        )
        EC2ParameterStore.set_env(django_parameters)
        ENVIRONMENT_VARIABLE_STRATEGY = EC2PARAMSTORE_4_ENVIRONMENT_VARIABLES
except Exception as e:
    print("Exception", e)

print('ENVIRONMENT_VARIABLE_STRATEGY in wsgi.py is', ENVIRONMENT_VARIABLE_STRATEGY)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vmi.settings')
application = get_wsgi_application()
