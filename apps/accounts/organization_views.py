import logging
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Organization
from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import permission_required

__author__ = "Alan Viars"

# Copyright Videntity Systems Inc.

logger = logging.getLogger('verifymyidentity_.%s' % __name__)


@login_required
def display_organization(request, organization_slug):
    org = get_object_or_404(Organization, slug=organization_slug)
    return render(request, 'organization.html', {"organization": org,
                                                 'signup_url': org.signup_url})


@login_required
@permission_required('organization_affiliation_request.can_approve_affiliation')
def remove_agent_from_organization(request, organization_slug, user_id):
    org = get_object_or_404(Organization, slug=organization_slug)
    user = get_object_or_404(get_user_model(), id=user_id)
    org.users.remove(user)
    msg = _('%s %s removed from %s.' %
            (user.first_name, user.last_name, org.name))
    messages.success(request, msg)
    return HttpResponseRedirect(reverse('display_organization', args=(org.slug,)))
