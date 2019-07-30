import logging
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Organization

# Copyright Videntity Systems Inc.

logger = logging.getLogger('verifymyidentity_.%s' % __name__)


@login_required
def display_organization(request, organization_slug):
    org = get_object_or_404(Organization, slug=organization_slug)
    return render(request, 'organization.html', {"organization": org,
                                                 'signup_url': org.signup_url})
