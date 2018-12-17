from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages
from ..accounts.models import UserProfile, Organization, OrganizationAffiliationRequest
from django.contrib.auth.decorators import login_required
from django.urls import reverse
# from django.contrib.auth.decorators import permission_required
from .forms import UserSearchForm

# Copyright Videntity Systems, Inc.


@login_required
def user_profile(request, subject=None):
    if not subject:
        user = request.user
    else:
        up = get_object_or_404(UserProfile, subject=subject)
        user = up.user
    context = {'user': user}
    template = 'profile.html'
    return render(request, template, context)


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

    context = {'organizations': request.user.userprofile.organizations}
    template = 'organization-user-dashboard.html'
    return render(request, template, context)


def authenticated_home(request):
    """Switch between annon, end user and organizational staff member."""
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
    context = {'name': name}
    template = 'index.html'
    return render(request, template, context)


def authenticated_enduser_home(request):

    name = _('End User Home')
    try:
        profile = request.user.userprofile
    except Exception:
        profile = UserProfile.objects.create(user=request.user)

    if not getattr(profile, 'ial_2', False):
        messages.warning(
            request,
            """Your identity has not been verified.
                <a href="">Verify your identity Now</a>""")

    context = {'name': name, 'profile': profile}
    template = 'authenticated-home.html'
    return render(request, template, context)


@login_required
def user_search(request):

    name = _('People Search')
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
