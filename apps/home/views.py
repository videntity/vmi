from django.shortcuts import render, get_object_or_404
from django.http import Http404
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.contrib import messages
from ..accounts.models import UserProfile, Organization, OrganizationAffiliationRequest
from ..ial.models import IdentityAssuranceLevelDocumentation
from django.contrib.auth.decorators import login_required
from django.urls import reverse
# from django.contrib.auth.decorators import permission_required
from .forms import UserSearchForm

from apps.accounts.sms_mfa_forms import LoginForm

# Copyright Videntity Systems, Inc.


@login_required
def user_profile(request, subject=None):
    if not subject:
        # Looking at your own record.
        user = request.user
    else:
        up = get_object_or_404(UserProfile, subject=subject)
        # Check permission that the user can view other profiles.
        if (request.user.userprofile.pk != up.pk
                and not request.user.has_perm('accounts.view_userprofile')):
            raise Http404()
        user = up.user
    ials = IdentityAssuranceLevelDocumentation.objects.filter(subject_user=user)
    context = {'user': user, 'settings': settings, "ials": ials}
    template = 'profile.html'
    return render(request, template, context)


@login_required
def authenticated_organization_home(request):
    up, created = UserProfile.objects.get_or_create(user=request.user)
    orgs_for_poc = Organization.objects.filter(point_of_contact=request.user)
    for o in orgs_for_poc:
        affiliation_requests = OrganizationAffiliationRequest.objects.filter(
            organization=o)
        for oar in affiliation_requests:

            msg = """%s %s is requesting to be an agent of %s.
                     Please <a href="%s">approve</a> or <a href="%s">deny</a>
                     the request.""" % (oar.user.first_name,
                                        oar.user.last_name,
                                        oar.organization.name,
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

    context = {'organizations': request.user.userprofile.organizations,
               'profile': up}
    template = 'organization-user-dashboard.html'
    return render(request, template, context)


def authenticated_home(request):
    """Switch between anon, end user and organizational staff member."""
    name = _('Home')
    if request.user.is_authenticated:
        # Create user profile if one does not exist,
        UserProfile.objects.get_or_create(user=request.user)

        # exists = Organization.users.all().exists()
        # check is the user is a member of any organization
        for o in Organization.objects.all():
            for u in o.users.all():
                if u == request.user:
                    return authenticated_organization_home(request)

        # If not in an org, then display end_user home.
        return authenticated_enduser_home(request)

    # User is not logged in.
    organizations = Organization.objects.all()
    context = {'name': name, 'organizations': organizations, 'login_form': LoginForm(initial=request.GET)}
    template = 'index.html'
    return render(request, template, context)


def authenticated_enduser_home(request):

    name = _('End User Home')
    try:
        profile = request.user.userprofile
    except Exception:
        profile = UserProfile.objects.create(user=request.user)

    if not profile.phone_verified:
        msg = """Your mobile phone has not been verified.
                <a href="%s">Verify your Mobile phone number now.</a>""" % (reverse('mobile_phone'))
        messages.warning(request, msg)

    context = {'name': name, 'profile': profile}
    template = 'authenticated-home.html'
    return render(request, template, context)


@login_required
def user_search(request):

    name = _('User Search')
    context = {'name': name}

    if request.method == 'POST':
        form = UserSearchForm(request.POST)
        if form.is_valid():
            search_results = form.save()
            context['search_results'] = search_results
            return render(request, 'user-search-results.html', context)

        else:
            # return the bound form with errors
            return render(request,
                          'generic/bootstrapform.html',
                          {'name': name, 'form': form})

    context['form'] = UserSearchForm
    template = 'generic/bootstrapform.html'
    return render(request, template, context)
