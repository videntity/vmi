from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from .models import UserProfile, MFACode
from django.conf import settings
from .sms_mfa_forms import LoginForm, MFACodeForm
from django.views.decorators.cache import never_cache
from ratelimit.decorators import ratelimit

# Copyright Videntity Systems Inc.

__author__ = "Alan Viars"


def mfa_code_confirm(request, uid):
    mfac = get_object_or_404(MFACode, uid=uid)
    user = mfac.user
    if request.method == 'POST':
        form = MFACodeForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']

            if code != mfac.code:
                mfac.tries_counter = mfac.tries_counter + 1
                if mfac.tries_counter > 3:
                    messages.error(
                        request,
                        _('Maximum tries reached.'
                          'The authentication attempt has been invalidated.'))
                    mfac.delete()
                else:
                    mfac.save()
                messages.error(
                    request,
                    _('The code supplied did not match what was sent.'
                      'Please try again.'))

                return render(
                    request, 'generic/bootstrapform.html', {'form': form})

            if user.is_active:
                # Fake backend here since its not needed.
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                # Else, just login as normal without MFA
                login(request, user)
                mfac.delete()
                next_param = request.GET.get('next', '')
                if next_param:
                    # If a next is in the URL, then go there
                    return HttpResponseRedirect(next_param)
                # otherwise just go to home.
                return HttpResponseRedirect(reverse('home'))
            else:
                # The user exists but is_active=False
                messages.error(
                    request,
                    _('Your account has not been activated.'
                      'Please check your email for a link to'
                      'activate your account.'))
                return render(
                    request, 'generic/bootstrapform.html', {'form': form})

        else:
            return render(request, 'generic/bootstrapform.html',
                          {'form': form})
    # this is a GET
    return render(request, 'generic/bootstrapform.html',
                  {'form': MFACodeForm()})


@never_cache
@ratelimit(key='ip', rate=settings.LOGIN_RATELIMIT, method='POST', block=True)
def mfa_login(request, slug=None):
    print('ggg')
    if not slug:
        login_template_name = settings.LOGIN_TEMPLATE_PICKER['default']
        name = settings.APPLICATION_TITLE
    else:
        login_template_name = settings.LOGIN_TEMPLATE_PICKER[slug]
        name = slug.replace('-', ' ')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)

            if user is not None:

                if user.is_active:
                    # Get User profile
                    up, g_o_c = UserProfile.objects.get_or_create(user=user)
                    login(request, user)
                    next_param = request.GET.get('next', '')
                    if next_param:
                        # If a next is in the URL, then go there
                        return HttpResponseRedirect(next_param)
                    # otherwise just go to home.
                    return HttpResponseRedirect(reverse('home'))
                else:
                    # The user exists but is_active=False
                    messages.error(request,
                                   _('Please check your email for a link to '
                                     'activate your account.'))
                    return render(request, login_template_name, {'form': form})
            else:
                messages.error(request, _('Invalid username or password.'))
                return render(request, login_template_name, {'form': form, 'name': name})
        else:
            return render(request, login_template_name, {'form': form, 'name': name})
    # this is a GET
    return render(request, login_template_name, {'form': LoginForm(), 'name': name})
