import logging
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from .models import Organization
from .staff_forms import StaffSignupForm
from django.conf import settings
from .emails import send_new_org_account_approval_email

# Copyright Videntity Systems Inc.

logger = logging.getLogger('verifymyidentity_.%s' % __name__)


def create_staff_account(request, organization_slug,
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

            messages.warning(request,
                             _("Your account must be approved "
                               "prior to logging in. A message has "
                               "been sent to your organization's "
                               "point of contact."))
            send_new_org_account_approval_email(to_user=org.point_of_contact,
                                                about_user=user)
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
