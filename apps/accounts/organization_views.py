import logging
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import permission_required
from .models import UserProfile, Organization
__author__ = "Alan Viars"

# Copyright Videntity Systems Inc.

logger = logging.getLogger('verifymyidentity_.%s' % __name__)


@login_required
def display_organization_agent_view(request, organization_slug):
    org = get_object_or_404(Organization, slug=organization_slug)
    if request.user not in org.users.all():
        raise Http404()
    return render(request, 'organization_agent_view.html', {"organization": org})


@login_required
def display_organization_member_view(request, organization_slug):
    org = get_object_or_404(Organization, slug=organization_slug)
    if request.user not in org.members.all():
        raise Http404()

    return render(request, 'organization_member_view.html', {"organization": org})


@login_required
def display_member_organizations(request, subject=None):
    name = _('Organizations')
    if not subject:
        # Looking at your own record.
        user = request.user
        up = get_object_or_404(UserProfile, user=user)
    else:
        up = get_object_or_404(UserProfile, subject=subject)
        # Check permission that the user can view other profiles.
        # if not request.user.has_perm('accounts.view_individualidentifier') and up.user != request.user:
        #    raise Http404()
        user = up.user
    organizations = Organization.objects.filter(members=user)
    context = {'user': user, 'organizations': organizations,
               'up': up, 'name': name}
    return render(request, 'organizations-table.html', context)


@login_required
@permission_required('organization_affiliation_request.can_approve_affiliation')
def remove_agent_from_organization(request, organization_slug, user_id):
    org = get_object_or_404(Organization, slug=organization_slug)
    user = get_object_or_404(get_user_model(), id=user_id)
    org.users.remove(user)
    msg = _('%s %s removed as agent of %s.' %
            (user.first_name, user.last_name, org.name))
    messages.success(request, msg)
    return HttpResponseRedirect(reverse('display_organization', args=(org.slug,)))


@login_required
def remove_member_from_organization(request, subject, organization_slug):
    org = get_object_or_404(Organization, slug=organization_slug)
    up = get_object_or_404(UserProfile, subject=subject)
    if request.user != up.user or request.user not in org.users.all():
        raise Http404("Not found.")

    org.members.remove(up.user)
    msg = _('%s %s removed as member of %s.' %
            (up.user.first_name, up.user.last_name, org.name))
    messages.success(request, msg)
    return HttpResponseRedirect(reverse('user_profile_subject', args=(up.subject,)))
