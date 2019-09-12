import logging
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from .models import UserProfile, ValidPasswordResetKey
from django.conf import settings
from .password_recovery_passphrase_generator import generate_password_recovery_phrase, passphrase_hash
from .password_recovery_passphrase_forms import RecoverPassowrdWithPassphraseForm
from django.views.decorators.cache import never_cache
from ratelimit.decorators import ratelimit
from .forms import PasswordResetForm
from django.contrib.auth import get_user_model

# Copyright Videntity Systems Inc.
__author__ = "Alan Viars"

logger = logging.getLogger('verifymyidentity_.%s' % __name__)


@login_required
def password_recovery_passphrase_home(request):
    name = _('Password Recovery Passphrase')
    up = get_object_or_404(UserProfile, user=request.user)
    exist = False
    if len(up.password_recovery_passphrase_hash) > 0:
        exist = True
        messages.warning(request, """A password recovery passphrase already exists.
          By clicking generate you will invalidate the existing recovery key.""")
    context = {'up': up, 'name': name, 'existing': exist}
    return render(request, 'password-recovery-passphrase.html', context)


@login_required
def generate_password_recovery_passphrase(request):
    name = _('Your Password Recovery Passphrase')
    password_recovery_phrase = generate_password_recovery_phrase()
    up = get_object_or_404(UserProfile, user=request.user)
    up.password_recovery_passphrase_hash = passphrase_hash(
        passphrase=password_recovery_phrase)
    up.save()
    messages.success(request, """A new password recovery passphrase has been generated.
                          Write it down or print this page so you can recover your account if you forget your actual password.
                          You can only see this one time or generate a new one which invalidates the old one.""")
    context = {
        'up': up, 'password_recovery_phrase': password_recovery_phrase, 'name': name}
    return render(request, 'display-password-recovery-passphrase.html', context)


@never_cache
@ratelimit(key='ip', rate=settings.LOGIN_RATELIMIT, method='POST', block=True)
def reset_password_with_recovery_passphrase(request):
    name = _('Reset Your Password With Your Recovery Passphrase')
    form = RecoverPassowrdWithPassphraseForm(request.POST)
    if request.method == 'POST':
        if form.is_valid():
            username = form.cleaned_data['username']
            user = get_object_or_404(get_user_model(), username=username)
            # if passes test send to password reset form
            vprk = ValidPasswordResetKey.objects.create(user=user)
            return HttpResponseRedirect(reverse('reset_password_after_passphrase_verified',
                                                args=(user.username, vprk.reset_password_key)))
        else:
            return render(request, 'generic/bootstrapform.html',
                          {'form': form, 'name': name})
    # this is a GET
    return render(request, 'generic/bootstrapform.html',
                  {'form': RecoverPassowrdWithPassphraseForm(),
                   'name': name})


@never_cache
@ratelimit(key='ip', rate=settings.LOGIN_RATELIMIT, method='POST', block=True)
def reset_password_after_passphrase_verified(request,  username, reset_password_key):
    name = "Reset Your Password"

    user = get_object_or_404(get_user_model(), username=username)
    vprk = get_object_or_404(ValidPasswordResetKey, user=user,
                             reset_password_key=reset_password_key)

    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            vprk.user.set_password(form.cleaned_data['password1'])
            vprk.user.save()
            vprk.delete()
            messages.success(request, _('Your password has been reset.'))
            return HttpResponseRedirect(reverse('mfa_login'))
        else:
            return render(request,
                          'generic/bootstrapform.html',
                          {'form': form, 'name': name})

    return render(request,
                  'generic/bootstrapform.html',
                  {'form': PasswordResetForm(),
                   'name': name})
