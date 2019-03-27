import logging
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from .models import Organization, OrganizationAffiliationRequest
from .staff_forms import StaffSignupForm
from django.conf import settings
from .emails import send_org_account_approved_email
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import permission_required
from django.http import HttpResponseForbidden

# Copyright Videntity Systems Inc.

logger = logging.getLogger('verifymyidentity_.%s' % __name__)


@login_required
@permission_required('organization_affiliation_request.can_approve_affiliation')
def approve_org_affiliation(request, organization_slug, username):

    org = get_object_or_404(Organization, slug=organization_slug)
    user = get_object_or_404(get_user_model(), username=username)
    oar = get_object_or_404(
        OrganizationAffiliationRequest,
        organization=org,
        user=user)
    if request.user != org.point_of_contact:
        return HttpResponseForbidden()

    org.users.add(user)
    org.save()
    oar.delete()
    msg = _("""%s %s is now affiliated with %s.""") % (user.first_name,
                                                       user.last_name,
                                                       org.name)
    send_org_account_approved_email(user)
    messages.success(request, msg)
    return HttpResponseRedirect(reverse('home'))


@login_required
@permission_required('organization_affiliation_request.can_approve_affiliation')
def deny_org_affiliation(request, organization_slug, username):
    org = get_object_or_404(Organization, slug=organization_slug)
    user = get_object_or_404(get_user_model(), username=username)
    oar = get_object_or_404(
        OrganizationAffiliationRequest,
        organization=org,
        user=user)
    if request.user != org.point_of_contact:
        return HttpResponseForbidden()
    oar.delete()
    msg = _("""You have canceled %s %s's affiliation request with %s.""") % (
        user.first_name, user.last_name, org.name)
    messages.success(request, msg)
    return HttpResponseRedirect(reverse('home'))


@login_required
def request_org_affiliation(request, organization_slug):
    org = get_object_or_404(Organization, slug=organization_slug)
    OrganizationAffiliationRequest.objects.create(
        organization=org, user=request.user)
    msg = _("""You have requested affiliation with  %s.""") % (org.name)
    messages.success(request, msg)
    return HttpResponseRedirect(reverse('home'))


def create_org_account(request, organization_slug,
                       service_title=settings.APPLICATION_TITLE):
    org = get_object_or_404(Organization, slug=organization_slug)
    name = _("Staff Signup for %s") % (org.name)
    if request.method == 'POST':
        form = StaffSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            if user.email:
                messages.success(request,
                                 _("Please "
                                   "check your email to confirm your email "
                                   "address."))

            messages.warning(
                request, _(
                    "Your affiliation with %s must be approved "
                    "prior to gaining access to certain functionality. A message has "
                    "been sent to your organization's "
                    "point of contact." %
                    (org.name)))

            return HttpResponseRedirect(reverse('home'))
        else:
            # return the bound form with errors
            return render(request,
                          'generic/bootstrapform.html',
                          {'name': name, 'form': form,
                           'service_title': service_title})
    else:
        # this is an HTTP  GET
        # Adding ability to pre-fill invitation_code and email
        # via GET parameters
        form_data = {
            'invitation_code': request.GET.get('invitation_code', ''),
            'email': request.GET.get('email', ''),
            'org_slug': org.slug}
        return render(request, 'generic/bootstrapform.html',
                      {'name': name, 'form':
                       StaffSignupForm(initial=form_data),
                       'service_title': service_title})
