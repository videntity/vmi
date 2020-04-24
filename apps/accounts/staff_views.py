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
from ..ial.models import IdentityAssuranceLevelDocumentation

# Copyright Videntity Systems Inc.

logger = logging.getLogger('verifymyidentity_.%s' % __name__)


@login_required
@permission_required('accounts.can_approve_affiliation')
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
    # Allow user to log in.
    user.is_active = True
    user.save()
    msg = _("""%s %s is now an agent of %s and may log in.""") % (user.first_name.title(),
                                                                  user.last_name.title(),
                                                                  org.name)
    send_org_account_approved_email(user, org)
    messages.success(request, msg)

    # Add IAL2 if option is selected.
    if org.auto_ial_2_for_agents:
        IdentityAssuranceLevelDocumentation.objects.create(
            subject_user=user,
            id_verify_description=settings.AUTO_IAL_2_DESCRIPTION,
            evidence=settings.AUTO_IAL_2_DEFAULT_CLASSIFICATION,
            note="IAL2 auto-applied to this agent account. %s." % (settings.AUTO_IAL_2_DESCRIPTION))
        # Add the user to default groups.
        for g in org.default_groups_for_agents.all():
            user.groups.add(g)

    return HttpResponseRedirect(reverse('home'))


@login_required
@permission_required('accounts.can_approve_affiliation')
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
        user.first_name.title(), user.last_name.title(), org.name)
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


def find_org_to_create_account(request):
    """When the user posts the find_org_to_create_account form, redirect to that page"""
    if request.method != 'POST' or not request.POST.get('organization_slug'):
        return HttpResponseRedirect(reverse('home'))
    else:
        org_slug = request.POST.get('organization_slug')
        return HttpResponseRedirect(reverse('create_org_account', args=[org_slug]))


def create_org_account(request, organization_slug,
                       service_title=settings.APPLICATION_TITLE):
    org = get_object_or_404(Organization, slug=organization_slug)
    name = _("Staff Signup for %s") % (org.name)
    if request.method == 'POST':
        form = StaffSignupForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            if user.email:
                messages.success(request, _("Your account was created."))
                messages.info(request, _("Please "
                                         "check your email to confirm your email "
                                         "address."))
            messages.warning(
                request, _(
                    """Your affiliation with %s must be approved by %s %s
                    before you may log in.
                    You will receive an email when your account is approved.""" %
                    (org.name, org.point_of_contact.first_name.title(),
                     org.point_of_contact.last_name.title())))
            return HttpResponseRedirect(reverse('home'))
        else:
            # return the bound form with errors
            messages.error(request, _("The form contained errors."))
            return render(request,
                          'generic/bootstrapform.html',
                          {'name': name, 'form': form,
                           'org_slug': org.slug,
                           'domain': org.domain,
                           'service_title': service_title})
    else:
        # this is an HTTP  GET
        # Adding ability to pre-fill invitation_code and email
        # via GET parameters
        form_data = {
            'invitation_code': request.GET.get('invitation_code', ''),
            'email': request.GET.get('email', ''),
            'org_slug': org.slug,
            'domain': org.domain}
        return render(request, 'generic/bootstrapform.html',
                      {'name': name, 'form':
                       StaffSignupForm(initial=form_data),
                       'service_title': service_title})
