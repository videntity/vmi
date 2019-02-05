from django.conf import settings
from django.utils.module_loading import import_string
from django.core.exceptions import ImproperlyConfigured

SESSION_KEY = '_mfa_device_id'
BACKEND_SESSION_KEY = '_mfa_device_backend'
REDIRECT_FIELD_NAME = 'next'


def load_backend(path):
    return import_string(path)()


def _get_backends(return_tuples=False):
    backends = []
    for backend_path in settings.VERIFICATION_BACKENDS:
        backend = load_backend(backend_path)
        backends.append((backend, backend_path) if return_tuples else backend)
    if not backends:
        raise ImproperlyConfigured(
            'No authentication backends have been defined. Does '
            'VERIFICATION_BACKENDS contain anything?'
        )
    return backends


def _get_device_session_key(backend, device_pk):
    return backend.get_device_model()._meta.pk.to_python(device_pk)


def verify(request, device, backend=None):
    request.session[SESSION_KEY] = device._meta.pk.value_to_string(device)
    if backend is not None:
        request.session[BACKEND_SESSION_KEY] = backend
    request.mfa_device = device


def user_has_mfa(user):
    for backend in _get_backends(return_tuples=False):
        if backend.is_enabled(user):
            return True
    return False


def get_device(request):
    device = None
    try:
        backend_path = request.session[BACKEND_SESSION_KEY]
        device_pk = request.session[SESSION_KEY]
    except KeyError:
        pass
    else:
        try:
            if backend_path in settings.VERIFICATION_BACKENDS:
                backend = load_backend(backend_path)
                device_id = _get_device_session_key(backend, device_pk)
                device = backend.get_device(device_id)
        except Exception:
            pass
    return device


def start_mfa(request):
    for backend, backend_path in _get_backends(return_tuples=True):
        if backend.is_enabled(request.user):
            request.session[BACKEND_SESSION_KEY] = backend_path
            return backend.start_verification(request)
