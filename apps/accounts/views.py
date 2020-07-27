import logging
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse
from django.contrib.auth import logout, login, authenticate
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from .forms import (PasswordResetForm, PasswordResetRequestForm)
from .models import UserProfile, ValidPasswordResetKey, ActivationKey
from .forms import (AccountSettingsForm,
                    SignupForm, DeleteAccountForm)

from .utils import validate_email_verify_key
from django.conf import settings
from django.views.decorators.cache import never_cache
from ratelimit.decorators import ratelimit

# Copyright Videntity Systems Inc.

logger = logging.getLogger('verifymyidentity_.%s' % __name__)


@never_cache
@ratelimit(key='ip', rate=settings.LOGIN_RATELIMIT, method='GET', block=True)
@ratelimit(key='ip', rate=settings.LOGIN_RATELIMIT, method='POST', block=True)
def reset_password(request):

    name = _('Change Password')
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = PasswordResetForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                request.user.set_password(data['password1'])
                request.user.save()
                user = authenticate(request=request,
                                    username=request.user.username,
                                    password=data['password1'])
                login(request, user)
                messages.success(request, _('Your password was updated.'))
                return HttpResponseRedirect(reverse('home'))
            else:
                return render(request, 'generic/bootstrapform.html',
                              {'form': form, 'name': name})
        # this is a GET
        return render(request, 'generic/bootstrapform.html',
                      {'form': PasswordResetForm(), 'name': name})
    else:
        return HttpResponseRedirect(reverse('home'))


def mylogout(request):
    logger.info("$s logged out.", request.user)
    logout(request)
    # messages.success(request, _('You have been logged out.'))
    return HttpResponseRedirect(reverse('home'))


@login_required
@ratelimit(key='ip', rate=settings.LOGIN_RATELIMIT, method='GET', block=True)
@ratelimit(key='ip', rate=settings.LOGIN_RATELIMIT, method='POST', block=True)
def delete_account(request):
    name = _('Delete Account Information')
    if request.method == 'POST':
        form = DeleteAccountForm(request.POST)
        if form.is_valid():
            request.user.delete()
            logout(request)
            messages.success(request, _('Your account has been deleted.'))
            return HttpResponseRedirect(reverse('home'))
    # This is a GET
    messages.warning(request, _(
        'You are about to permanently delete your account. This action cannot be undone.'))
    return render(request,
                  'generic/bootstrapform.html',
                  {'name': name, 'form': DeleteAccountForm()})


@login_required
def account_settings(request, subject=None):
    if not subject:
        # Looking at your own record.
        user = request.user
        up = get_object_or_404(UserProfile, user=user)
        name = _('Edit Your Basic Profile Information')
    else:
        up = get_object_or_404(UserProfile, subject=subject)
        # Check permission that the user can view other profiles.
        if not request.user.has_perm('accounts.change_userprofile'):
            raise Http404()
        user = up.user
        name = _("Edit Basic Profile Information for %s" % (up))

    if request.method == 'POST':
        form = AccountSettingsForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            # update the user info
            user.username = data['username']
            user.email = data['email']
            user.first_name = data['first_name']
            user.last_name = data['last_name']
            user.save()
            # update the user profile
            up.nickname = data['nickname']
            up.sex = data['sex']
            up.gender_identity = data['gender_identity']
            up.gender_identity_custom_value = data[
                'gender_identity_custom_value']
            up.middle_name = data['middle_name']
            up.birth_date = data['birth_date']
            up.website = data['website']
            up.save()
            messages.success(request, _(
                'Your account settings have been updated.'))
            if subject:
                return HttpResponseRedirect(reverse('account_settings_subject', args=(subject,)))
            return HttpResponseRedirect(reverse('account_settings'))
        else:
            # the form had errors
            return render(request,
                          'account-settings.html',
                          {'form': form, 'name': name, 'up': up})

    # this is an HTTP GET
    form = AccountSettingsForm(
        initial={
            'username': user.username,
            'last_name': user.last_name,
            'first_name': user.first_name,
            'email': user.email,
            'mobile_phone_number': up.mobile_phone_number,
            'sex': up.sex,
            'website': up.website,
            'gender_identity': up.gender_identity,
            'gender_identity_custom_value': up.gender_identity_custom_value,
            'birth_date': up.birth_date,
            'nickname': up.nickname,
            'middle_name': up.middle_name,
        }
    )
    return render(request,
                  'account-settings.html',
                  {'name': name, 'form': form, 'up': up})


def create_account(request, service_title=settings.APPLICATION_TITLE):
    name = _("Signup for %s") % (service_title)
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            # get the username and password
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            # authenticate user then login
            user = authenticate(username=username, password=password)
            login(request, user)
            redirect_url = request.GET.get('next', reverse('home'))
            return HttpResponseRedirect(redirect_url)
        else:
            # return the bound form with errors
            return render(request,
                          'generic/bootstrapform.html',
                          {'name': name, 'form': form,
                           'service_title': service_title})
    else:
        # this is an HTTP  GET
        # Adding ability to pre-fill invitation_code and email
        # via GET paramters
        form_data = {'invitation_code': request.GET.get('invitation_code', ''),
                     'email': request.GET.get('email', '')}
        return render(request,
                      'generic/bootstrapform.html',
                      {'name': name, 'form': SignupForm(initial=form_data),
                       'service_title': service_title})


def password_reset_email_verified(request, reset_password_key=None):
    name = "Reset Your Password"
    vprk = get_object_or_404(ValidPasswordResetKey,
                             reset_password_key=reset_password_key)
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            vprk.user.set_password(form.cleaned_data['password1'])
            vprk.user.save()
            vprk.delete()
            logout(request)
            messages.success(request, _('Your password has been reset.'))
            return HttpResponseRedirect(reverse('mfa_login'))
        else:
            return render(request,
                          'generic/bootstrapform.html',
                          {'form': form, 'name': name,
                           'reset_password_key': reset_password_key})

    return render(request,
                  'generic/bootstrapform.html',
                  {'form': PasswordResetForm(),
                   'name': name,
                   'reset_password_key': reset_password_key})


def activation_verify(request, activation_key):
    try:
        vc = ActivationKey.objects.get(key=activation_key)
        user = vc.user
    except ActivationKey.DoesNotExist:
        user = None

    if validate_email_verify_key(activation_key):
        messages.success(request,
                         _('Your email has been verified.'))
        if user:
            if not user.is_active:
                messages.warning(request,
                                 _("""Your account is not active so you may not log
                           in at this time. Your account may require approval before logging in or
                         your account has been administratively deactivated."""))

    else:
        messages.error(request,
                       'This key does not exist or has already been used.')
    return HttpResponseRedirect(reverse('home'))


@never_cache
@ratelimit(key='ip', rate=settings.LOGIN_RATELIMIT, method='GET', block=True)
@ratelimit(key='ip', rate=settings.LOGIN_RATELIMIT, method='POST', block=True)
def forgot_password(request):
    name = _('Forgot Password?')
    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)

        if form.is_valid():
            data = form.cleaned_data
            try:
                u = User.objects.get(email=data['email'])
            except(User.DoesNotExist):
                try:
                    u = User.objects.get(username=data['email'])
                except(User.DoesNotExist):
                    messages.error(
                        request,
                        'A user with the email or username supplied '
                        'does not exist.')
                    return HttpResponseRedirect(reverse('forgot_password'))
            logger.info("Forgot password request sent to %s", u.email)

            ValidPasswordResetKey.objects.create(user=u)
            # success - user found so ask some question
            messages.success(request,
                             'Please check your email for a link to reset your password.')

            return HttpResponseRedirect(reverse('home'))
        else:
            return render(request,
                          'generic/bootstrapform.html',
                          {'name': name, 'form': form})
    else:
        return render(request,
                      'generic/bootstrapform.html',
                      {'name': name, 'form': PasswordResetRequestForm()})
