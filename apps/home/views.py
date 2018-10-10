from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages

# Copyright Videntity Systems, Inc.


def authenticated_home(request):
    if request.user.is_authenticated:
        name = _('Authenticated Home')
        try:
            profile = request.user.userprofile
        except Exception:
            profile = None

        # this is a GET
        context = {'name': name}
        template = 'authenticated-home.html'
        if not getattr(profile, 'email_verified', False):
            messages.warning(
                request,
                """Your email has not been verified.
                <a href="">Verify it Now</a>""")

        if not getattr(profile, 'mobile_phone_verified', False):
            messages.warning(
                request,
                """Your mobile phone number has not been verified.
                <a href="">Verify it Now</a>""")

        if not getattr(profile, 'ial_2', False):
            messages.warning(
                request,
                """Your identity has not been verified.
                <a href="">Verify it Now</a>""")

    else:
        name = _('Anon Home')
        context = {'name': name}
        template = 'index.html'
    return render(request, template, context)
