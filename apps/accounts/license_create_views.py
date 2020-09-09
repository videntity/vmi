import logging
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import login_required
from .models import IDCardConfirmation
from .barcode_forms import ConfirmForm
import json
from django.contrib.auth import authenticate, login

# Copyright Videntity Systems Inc.

logger = logging.getLogger('verifymyidentity_.%s' % __name__)


@login_required
def complete_barcode_signup(request):
    HttpResponse("ok")


def member_confirm(request, confirmation_uuid):
    idc = get_object_or_404(IDCardConfirmation, confirmation_uuid=confirmation_uuid)
    name = _("Complete Your Account Setup ....")
    if request.method == 'POST':
        form = ConfirmForm(request.POST, request.FILES)
        if form.is_valid():
            print("create user", "id verification", "address")
            form.save()
            user = authenticate(username=form.cleaned_data['username'],
                                password=form.cleaned_data['password1'],)
            login(request, user)
            messages.success(request, _("Account activated."))
            if not user.email:
                messages.warning(request, _(
                    "Please add an email so we can send you important updates."))
            else:
                messages.warning(request, _(
                    "Please verify your email address in settings."))

            return HttpResponseRedirect(reverse('home'))

        else:
            # return the bound form with errors
            messages.error(request, _("The form contained errors."))
            return render(request,
                          'generic/bootstrapform.html',
                          {'name': name, 'form': form})
    else:
        # this is an HTTP  GET
        # Adding ability to pre-fill invitation_code and email
        # via GET parameters

        barcode_details = json.loads(idc.details)
        form_data = {'first_name': barcode_details['first_name'],
                     'last_name': barcode_details['last_name'],
                     'mobile_phone_number': idc.mobile_phone_number,
                     'sex': barcode_details['sex_standardized'],
                     'birth_date': barcode_details['birthdate_standardized'],
                     'barcode_details': idc.details,
                     'org_slug': idc.org_slug,
                     'confirmation_uuid': confirmation_uuid}
        return render(request, 'generic/bootstrapform.html',
                      {'name': name, 'form': ConfirmForm(initial=form_data)})
