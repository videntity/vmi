import logging
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from .models import UserProfile
from django.contrib.auth import get_user_model
from django.conf import settings
from .sms_mfa_forms import LoginForm
from django.views.decorators.cache import never_cache
from ratelimit.decorators import ratelimit

# Copyright Videntity Systems Inc.

__author__ = "Alan Viars"

logger = logging.getLogger(__name__)


@never_cache
@ratelimit(key='ip', rate=settings.LOGIN_RATELIMIT, method='POST', block=True)
def mfa_login(request, slug=None):
    if not slug:
        login_template_name = settings.LOGIN_TEMPLATE_PICKER['default']
        name = settings.APPLICATION_TITLE
    else:
        login_template_name = settings.LOGIN_TEMPLATE_PICKER[slug]
        name = slug.replace('-', ' ')

    context = {
        'name': name,
        'next': request.GET.get('next', '') or request.POST.get('next', ''),
        'login_form': LoginForm(initial=request.GET),
    }

    logger.debug('mfa_login(): context = %r', context)

    if request.method == 'POST':
        context['login_form'] = LoginForm(request.POST)
        if context['login_form'].is_valid():
            username = context['login_form'].cleaned_data['username']
            password = context['login_form'].cleaned_data['password']
            user = authenticate(username=username, password=password)
            try:
                User = get_user_model()
                myuser = User.objects.get(username=username)
            except User.DoesNotExist:
                myuser = None

            if myuser:
                if not myuser.is_active:
                    messages.error(request, _("""Your account is not active so you may not log
                           in at this time. Your account may require approval before logging in or
                         your account has been administratively deactivated."""))
                    return HttpResponseRedirect(reverse('home'))

            if user is not None:
                if user.is_active:
                    # Get User profile
                    up, g_o_c = UserProfile.objects.get_or_create(user=user)
                    login(request, user)
                    if context['next']:
                        logger.debug('redirect to %r' % context['next'])
                        return HttpResponseRedirect(context['next'])
                    # otherwise just go to home.
                    logger.debug('redirect to home')
                    return HttpResponseRedirect(reverse('home'))
                else:
                    # The user exists but is_active=False
                    messages.error(
                        request,
                        _(
                            'Please check your email for a link to '
                            'activate your account.'
                        ),
                    )
            else:
                messages.error(request, _('Invalid username or password.'))

    logger.debug('render login_form: %r %r', login_template_name, context)
    return render(request, login_template_name, context)
