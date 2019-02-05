import logging
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
# from .emails import send_new_org_account_approval_email
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from ..accounts.models import UserProfile
from .forms import InPersonIdVerifyForm, DowngradeIdentityAssuranceLevelForm
from .models import IdentityAssuranceLevelDocumentation

# Copyright Videntity Systems Inc.

logger = logging.getLogger('verifymyidentity_.%s' % __name__)


@login_required
@permission_required('ial.change_identityassuranceleveldocumentation')
def inperson_id_verify(request, subject):
    up = get_object_or_404(UserProfile, subject=subject)
    if request.user == up.user:
        raise Http404("You cannot upgrade your own identity assurance level.")

    ial_d, created = IdentityAssuranceLevelDocumentation.objects.get_or_create(
        subject_user=up.user)
    name = _("Verify Identity for %s %s (%s)") % (up.user.first_name, up.user.last_name,
                                                  up.subject)
    if request.method == 'POST':
        form = InPersonIdVerifyForm(request.POST, instance=ial_d)
        if form.is_valid():
            ial_doc = form.save(commit=False)
            ial_doc.subject_user = up.user
            ial_doc.verifying_user = request.user
            ial_doc.action = "1-TO-2"
            ial_doc.save()
            messages.success(
                request, _(
                    "You have verified %s %s's (%s ) identity." % (up.user.first_name,
                                                                   up.user.last_name,
                                                                   up.subject)))
            return HttpResponseRedirect(reverse('user_profile_subject', args=(up.subject,)))
        else:
            # return the bound form with errors
            return render(request,
                          'generic/bootstrapform.html',
                          {'name': name, 'form': form})
    else:
        # this is an HTTP  GET
        return render(request, 'generic/bootstrapform.html',
                      {'name': name, 'form':
                       InPersonIdVerifyForm(instance=ial_d)})


@login_required
@permission_required('ial.change_identityassuranceleveldocumentation')
def two_to_one_downgrade(request, subject):
    up = get_object_or_404(UserProfile, subject=subject)
    if request.user == up.user:
        raise Http404(
            "You cannot downgrade your own identity assurance level.")
    ial_d, created = IdentityAssuranceLevelDocumentation.objects.get_or_create(
        subject_user=up.user)
    name = _("Verify Identity for %s %s (%s)") % (up.user.first_name, up.user.last_name,
                                                  up.subject)
    if request.method == 'POST':
        form = DowngradeIdentityAssuranceLevelForm(
            request.POST, instance=ial_d)
        if form.is_valid():
            ial_doc = form.save(commit=False)
            ial_doc.subject_user = up.user
            ial_doc.verifying_user = request.user
            ial_doc.action = "2-TO-1"
            ial_doc.save()
            messages.success(
                request, _(
                    "You downgraded the identity assurance level to 1 for %s %s (%s)." % (up.user.first_name,
                                                                                          up.user.last_name,
                                                                                          up.subject)))
            return HttpResponseRedirect(reverse('user_profile_subject', args=(up.subject,)))
        else:
            # return the bound form with errors
            return render(request,
                          'generic/bootstrapform.html',
                          {'name': name, 'form': form})
    else:
        # this is an HTTP  GET
        return render(request, 'generic/bootstrapform.html',
                      {'name': name, 'form':
                       DowngradeIdentityAssuranceLevelForm(instance=ial_d)})
