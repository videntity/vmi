from collections import OrderedDict
from django.conf import settings
from oauth2_provider.models import Application
# from ..dot_ext.models import Application


def test_setup(include_client_secret=True):

    response = OrderedDict()
    oa2client = Application.objects.get(name="TestApp")
    response['client_id'] = oa2client.client_id
    if include_client_secret:
        response['client_secret'] = oa2client.client_secret
    host = getattr(settings, 'HOSTNAME_URL', 'http://localhost:8000')
    if not (host.startswith("http://") or host.startswith("https://")):
        host = "https://" + host
    response['resource_uri'] = host
    response['redirect_uri'] = '%s/testclient/callback' % host
    response['authorization_uri'] = '%s/o/authorize/' % host
    response['token_uri'] = '%s/o/token/' % host
    response['userinfo_uri'] = '%s/accounts/userprofile' % host
    response['patient_uri'] = '%s/fhir/baseDstu3/Patient/' % host
    response['eob_uri'] = '%s/fhir/baseDstu3/ExplanationOfBenefit/' % host
    response['coverage_uri'] = '%s/fhir/baseDstu3/Coverage/' % host
    response['condition_uri'] = '%s/fhir/baseDstu3/Condition/' % host
    return(response)


def get_client_id_and_secret():
    oa2client = Application.objects.get(name="TestApp")
    return ({'client_id': oa2client.client_id,
             'client_secret': oa2client.client_secret})


def get_client_secret():
    oa2client = Application.objects.get(name="TestApp")
    return oa2client.client_secret
