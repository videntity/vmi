import logging
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from .models import UserProfile, PhoneVerifyCode
from .phone_forms import PhoneForm, PhoneVerifyCodeForm

# Copyright Videntity Systems Inc.

logger = logging.getLogger('verifymyidentity_.%s' % __name__)


@login_required
def verify_mobile_phone_number(request, uid):
    name = _('Verify your Mobile Phone Number')
    up = get_object_or_404(UserProfile, user=request.user)
    pvc = get_object_or_404(PhoneVerifyCode, uid=uid)
    if request.method == 'POST':
        form = PhoneVerifyCodeForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            if code != pvc.code:
                pvc.tries_counter = pvc.tries_counter + 1
                if pvc.tries_counter > 3:
                    messages.error(
                        request,
                        _('Maximum tries reached.'
                          'The authentication attempt has been invalidated.'))
                    pvc.delete()
                else:
                    pvc.save()
                messages.error(
                    request,
                    _('The code supplied did not match what was sent.'
                      'Please try again.'))
                return render(
                    request, 'generic/bootstrapform.html', {'form': form})
            else:
                # The code matched.
                up.phone_verified = True
                up.save()
                pvc.delete()
                messages.info(request,
                              _('Your mobile phone number was verified.'))
            return HttpResponseRedirect(reverse('home'))

        else:
            # the form had errors
            return render(request,
                          'generic/bootstrapform.html',
                          {'form': form, 'name': name})

    return render(request, 'generic/bootstrapform.html',
                  {'form': PhoneVerifyCodeForm(), 'name': name})


@login_required
def mobile_phone(request):
    name = _('Mobile Phone and Verification')
    up = get_object_or_404(UserProfile, user=request.user)

    if request.method == 'POST':
        form = PhoneForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            # update the user info
            if up.mobile_phone_number == data['mobile_phone_number'] and \
                    up.phone_verified is True:
                # Nothing to do. The number is unchanged and already verified
                messages.info(request,
                              _('Your number has already been verified.'))
                return HttpResponseRedirect(reverse('mobile_phone'))
            elif (up.mobile_phone_number != data['mobile_phone_number'] or up.phone_verified is False) and \
                    data['verify_now'] is True:
                # Save the new number
                up.mobile_phone_number = data['mobile_phone_number']
                up.phone_verified = False
                up.save()

                # Send a verification text
                pvc = PhoneVerifyCode.objects.create(user=request.user)
                messages.info(request,
                              _('A code was just sent to the number provided. Please enter it here.'))
                return HttpResponseRedirect(reverse('verify_mobile_phone_number', args=(pvc.uid,)))
        else:
            # the form had errors
            return render(request,
                          'generic/bootstrapform.html',
                          {'form': form, 'name': name})

    # this is an HTTP GET
    form = PhoneForm(
        initial={
            'mobile_phone_number': up.mobile_phone_number,
        }
    )

    return render(request, 'generic/bootstrapform.html',
                  {'form': form, 'name': name})
