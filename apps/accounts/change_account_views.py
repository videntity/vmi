import logging
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from .models import UserProfile
from django.contrib.auth.decorators import permission_required

# Copyright Videntity Systems Inc.

logger = logging.getLogger('verifymyidentity_.%s' % __name__)


@login_required
@permission_required('auth.change_user')
def activate_subject(request, subject):
    up = get_object_or_404(UserProfile, subject=subject)
    up.user.is_active = True
    up.user.save()
    msg = _("Account for %s %s's account was activated by %s %s." % (
        up.user.first_name.title(), up.user.last_name.title(),
        request.user.first_name.title(), request.user.last_name.title()))
    logger.info(msg)
    messages.success(request, _('Account activated.'))
    return HttpResponseRedirect(reverse('user_profile_subject', args=(up.subject,)))


@login_required
@permission_required('auth.change_user')
def deactivate_subject(request, subject):
    up = get_object_or_404(UserProfile, subject=subject)
    up.user.is_active = False
    up.user.save()
    msg = _("Account for %s %s's account was deactivated by %s %s." % (
        up.user.first_name.title(), up.user.last_name.title(),
        request.user.first_name.title(), request.user.last_name.title()))
    logger.info(msg)
    messages.success(request, _('Account deactivated.'))
    return HttpResponseRedirect(reverse('user_profile_subject', args=(up.subject,)))
