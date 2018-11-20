# error_handlers.py
from urllib.parse import urlsplit, urlunsplit
from oauthlib.oauth2.rfc6749.grant_types import OIDCNoPrompt
from django.utils.deprecation import MiddlewareMixin
from django.http.request import QueryDict
from django.contrib.auth.views import LogoutView
from django.shortcuts import redirect
from .exceptions import AuthenticationRequired


class AuthenticationRequiredExceptionMiddleware(MiddlewareMixin):
    def process_exception(self, request, exception):
        if isinstance(exception, AuthenticationRequired):
            return LogoutView.as_view(next_page=exception.next)(request)


class OIDCNoPromptMiddleware(MiddlewareMixin):

    def process_exception(self, request, exception):
        if isinstance(exception, OIDCNoPrompt):
            scheme, netloc, path, query, fragment = urlsplit(request.GET.get("redirect_uri", None))  # noqa
            q = QueryDict(query, mutable=True)
            q.update({"error": "login_required,interaction_required"})
            redirect_uri = urlunsplit((scheme,
                                       netloc,
                                       path,
                                       q.urlencode(),
                                       fragment,))
            return redirect(redirect_uri)
