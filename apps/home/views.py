from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages
from ..accounts.models import UserProfile, Organization, OrganizationAffiliationRequest
from django.contrib.auth.decorators import login_required
from django.urls import reverse

# Copyright Videntity Systems, Inc.


@login_required
def authenticated_organization_home(request):

    orgs_for_poc = Organization.objects.filter(point_of_contact=request.user)

    for o in orgs_for_poc:
        affiliation_requests = OrganizationAffiliationRequest.objects.filter(
            organization=o)
        for oar in affiliation_requests:

            msg = """%s %s is requesting to be affiliated with your organization.
                     Please <a href="%s">approve</a> or <a href="%s">deny</a>
                     the request.""" % (oar.user.first_name,
                                        oar.user.last_name,
                                        reverse(
                                            'approve_org_affiliation',
                                            args=(
                                                oar.organization.slug,
                                                oar.user.username)),
                                        reverse(
                                            'deny_org_affiliation',
                                            args=(
                                                oar.organization.slug,
                                                oar.user.username)))

            messages.info(request, msg)

    context = {}
    template = 'authenticated-home.html'
    return render(request, template, context)


def authenticated_home(request):
    if request.user.is_authenticated:
        name = _('Authenticated Home')
        try:
            profile = request.user.userprofile
        except Exception:
            profile = UserProfile.objects.create(user=request.user)

        org_count = profile.organizations.all().count()

        if org_count > 0:
            return authenticated_organization_home(request)

        # this is a GET
        context = {'name': name}
        template = 'authenticated-home.html'
        if not getattr(request.user, 'email', ''):
            messages.warning(
                request,
                """Please consider adding an email to your account.
                <a href="">Add it Now</a>""")

        if not getattr(
            profile,
            'email_verified',
                False) and request.user.email:

            messages.warning(
                request,
                """Your email has not been verified.
                    <a href="">Verify it Now</a>""")

        if not getattr(profile, 'phone_verified', False):
            messages.warning(
                request,
                """Your mobile phone number has not been verified.
                <a href="">Verify your mobile phone number now</a>""")

        if not getattr(profile, 'ial_2', False):
            messages.warning(
                request,
                """Your identity has not been verified.
                <a href="">Verify your identity Now</a>""")
        context = {'name': name, 'profile': profile}

    else:
        name = _('Anon Home')
        context = {'name': name}
        template = 'index.html'
    return render(request, template, context)
