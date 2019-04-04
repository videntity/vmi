from django.conf import settings

assert getattr(settings, 'ATOMIC_REQUESTS', False), "Use of this API package requires ATOMIC_REQUESTS to be enabled to ensure no cases of partial success occure"  # noqa
