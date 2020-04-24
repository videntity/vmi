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
from .forms import SelectVerificationTypeIDCardForm, IDCardForm
from .models import IdentityAssuranceLevelDocumentation
from django.utils.safestring import mark_safe

# Copyright Videntity Systems Inc.

logger = logging.getLogger('verifymyidentity_.%s' % __name__)


@login_required
@permission_required('ial.change_identityassuranceleveldocumentation')
def delete_id_verify(request, id):
    ial_d = get_object_or_404(IdentityAssuranceLevelDocumentation, pk=id)
    msg = "Identity verification evidence for %s %s removed by %s %s." % (ial_d.subject_user.first_name.title(),
                                                                          ial_d.subject_user.last_name.title(),
                                                                          request.user.first_name.title(),
                                                                          request.user.last_name.title())
    logger.info(msg)
    messages.success(request, _(msg))
    user = ial_d.subject_user
    ial_d.delete()
    up = UserProfile.objects.get(user=user)
    up.verifying_agent_email = ""
    up.save()
    return HttpResponseRedirect(reverse('user_profile_subject', args=(up.subject,)))


@login_required
@permission_required('ial.change_identityassuranceleveldocumentation')
def enter_id_card_info(request, id):

    ial_d = get_object_or_404(IdentityAssuranceLevelDocumentation, pk=id)
    if request.user == ial_d.subject_user:
        raise Http404("You cannot upgrade your own identity assurance level.")
    up = get_object_or_404(UserProfile, user=ial_d.subject_user)
    name = _("Complete the ID card / evidence details for %s") % (up)

    if request.method == 'POST':
        form = IDCardForm(request.POST, request.FILES, instance=ial_d)
        if form.is_valid():
            ial_doc = form.save(commit=False)
            ial_doc.subject_user = up.user
            ial_doc.verifying_user = request.user
            ial_doc.save()
            up.verifying_agent_email = request.user.email
            up.save()
            messages.info(request, _("Identity verification details updated."))
            return HttpResponseRedirect(reverse('user_profile_subject', args=(up.subject,)))
        else:
            # return the bound form with errors
            return render(request,
                          'generic/bootstrapform.html',
                          {'name': name, 'form': form})
    else:
        # this is an HTTP  GET
        initial = {}
        if ial_d.evidence == "ONE-SUPERIOR-OR-STRONG-PLUS-1":
            initial["id_document_type"] = "driving_permit"
        if ial_d.evidence in ("ONE-SUPERIOR-OR-STRONG-PLUS-2",
                              "ONE-SUPERIOR-OR-STRONG-PLUS-3",
                              "TWO-STRONG-1"):
            initial["id_document_type"] = "idcard"
        if ial_d.evidence == "ONE-SUPERIOR-OR-STRONG-PLUS-4":
            initial["id_document_type"] = "passport"
        if ial_d.evidence in ("ONE-SUPERIOR-OR-STRONG-PLUS-5",
                              "ONE-SUPERIOR-OR-STRONG-PLUS-6"):
            initial["id_document_type"] = "us_health_insurance_card"

        msg = _("""Add evidence details here or continue to
                  <a href="%s">%s's</a> profile.""" % (
            reverse('user_profile_subject', args=(up.subject,)), up)
        )
        messages.info(request, _(mark_safe(msg)))
        if not up.user.is_active:
            msg = _("""%s account is not active and may not login.
                       <a href="%s">Activate now</a>?""" % (up,
                                                            reverse('activate_subject', args=(up.subject,))))
            messages.warning(request, _(mark_safe(msg)))

        return render(request, 'generic/bootstrapform.html',
                      {'name': name, 'form':
                       IDCardForm(instance=ial_d, initial=initial)})


@login_required
@permission_required('ial.change_identityassuranceleveldocumentation')
def verify_id_with_card(request, subject):
    up = get_object_or_404(UserProfile, subject=subject)
    if request.user == up.user:
        raise Http404(
            "You cannot enter information about your own identity assurance level.")

    ial_d = IdentityAssuranceLevelDocumentation.objects.create(
        subject_user=up.user)
    name = _("Verify the identity of %s") % (up)
    if request.method == 'POST':
        form = SelectVerificationTypeIDCardForm(
            request.POST, request.FILES, instance=ial_d)
        if form.is_valid():
            ial_doc = form.save(commit=False)
            ial_doc.subject_user = up.user
            ial_doc.verifying_user = request.user
            ial_doc.save()
            msg = _("""The identity for %s %s is now verified.""" % (ial_doc.subject_user.first_name.title(),
                                                                     ial_doc.subject_user.last_name.title()))
            messages.success(request, _(msg))
            return HttpResponseRedirect(reverse('enter_id_card_info', args=(ial_doc.pk,)))
        else:
            # return the bound form with errors
            return render(request,
                          'generic/bootstrapform.html',
                          {'name': name, 'form': form})
    else:
        # this is an HTTP  GET

        messages.warning(request, _("""NOTE: Complete this form after you have inspected evidence.
                                       Optionally, you may add more details about the evidence on the next screen."""))

        return render(request, 'generic/bootstrapform.html',
                      {'name': name, 'form':
                       SelectVerificationTypeIDCardForm(instance=ial_d)})
