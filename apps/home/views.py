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
from django.contrib.auth.decorators import permission_required
from apps.accounts.sms_mfa_forms import LoginForm
from django.utils.safestring import mark_safe

# Copyright Videntity Systems, Inc.


def select_org_for_account_create(request, user_type="member"):
    """Select an org for create an account."""
    template = 'select-org-for-member.html'
    organizations = Organization.objects.filter(status="ACTIVE")
    context = {'organizations': organizations}
    if user_type == "agent":
        template = 'select-org-for-agent.html'
    return render(request, template, context)


@login_required
def authenticated_organization_home(request):
    up, created = UserProfile.objects.get_or_create(user=request.user)
    orgs_for_poc = Organization.objects.filter(point_of_contact=request.user)
    for o in orgs_for_poc:
        affiliation_requests = OrganizationAffiliationRequest.objects.filter(
            organization=o)
        for oar in affiliation_requests:

            msg = """%s %s (%s) is requesting to be an agent of %s.
                     Please <a href="%s">approve</a> or <a href="%s">deny</a>
                     the request.""" % (oar.user.first_name,
                                        oar.user.last_name,
                                        oar.user.email,
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

# Routes to auth or non auth


def home(request):
    """Switch between anon, end user and organizational staff member."""
    name = _('Home')
    template = settings.PUBLIC_HOME_TEMPLATE
    if request.user.is_authenticated:
        # Create user profile if one does not exist,
        UserProfile.objects.get_or_create(user=request.user)
        return authenticated_enduser_home(request)

    # User is not logged in.
    organizations = Organization.objects.filter(status="ACTIVE")
    context = {'name': name, 'organizations': organizations,
               'login_form': LoginForm(initial=request.GET)}

    return render(request, template, context)


@login_required
def authenticated_enduser_home(request):
    name = _('Enduser Home')
    template = settings.AUTHENTICATED_HOME_TEMPLATE
    up, created = UserProfile.objects.get_or_create(user=request.user)
    orgs_for_poc = Organization.objects.filter(point_of_contact=request.user)

    # Show agent approve/deny message.
    for o in orgs_for_poc:
        affiliation_requests = OrganizationAffiliationRequest.objects.filter(
            organization=o)
        for oar in affiliation_requests:
            vup, g_or_c = UserProfile.objects.get_or_create(user=oar.user)
            msg = """<a href="%s">%s %s (%s)</a> is requesting to be an agent of %s.
                     Please <a href="%s">approve</a> or <a href="%s">deny</a>
                     the request.""" % (reverse('user_profile_subject',
                                                args=(vup.subject,)),
                                        oar.user.first_name,
                                        oar.user.last_name,
                                        oar.user.email,
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
    if not up.phone_verified:
        msg = """Your mobile phone has not been verified.
                <a href="%s">Verify your Mobile phone number now.</a>""" % (reverse('mobile_phone'))
        messages.warning(request, msg)

    context = {'name': name, 'profile': up}

    return render(request, template, context)


@login_required
@permission_required('ial.change_identityassuranceleveldocumentation')
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


@login_required
def user_profile(request, subject=None):
    if not subject:
        # Looking at your own record.
        user = request.user
    else:
        up = get_object_or_404(UserProfile, subject=subject)
        # Check permission that the user can view another user's profiles.
        if (request.user.userprofile.pk != up.pk
                and not request.user.has_perm('accounts.view_userprofile')):
            raise Http404()
        user = up.user
    ials = IdentityAssuranceLevelDocumentation.objects.filter(
        subject_user=user)
    context = {'user': user, 'settings': settings, "ials": ials}
    template = 'profile.html'

    if not up.user.is_active:
        msg = _("""%s account is not active and may not log in.
                       <a href="%s">Activate now</a>?""" % (up,
                                                            reverse('activate_subject', args=(up.subject,))))
        messages.warning(request, _(mark_safe(msg)))

    return render(request, template, context)
