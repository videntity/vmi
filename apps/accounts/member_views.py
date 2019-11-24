import logging
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from .models import Organization, UserProfile
from .member_forms import MemberSignupForm
from django.conf import settings
from django.utils.safestring import mark_safe


# Copyright Videntity Systems Inc.

logger = logging.getLogger('verifymyidentity_.%s' % __name__)


def find_org_to_create_member_account(request):
    """When the user posts the find_org_to_create_account form, redirect to that page"""
    if request.method != 'POST' or not request.POST.get('organization_slug'):
        return HttpResponseRedirect(reverse('home'))
    else:
        org_slug = request.POST.get('organization_slug')
        return HttpResponseRedirect(reverse('create_member_account', args=[org_slug]))


def create_member_account(request, organization_slug,
                          service_title=settings.APPLICATION_TITLE):
    org = get_object_or_404(Organization, slug=organization_slug)
    name = _("Member Signup via %s") % (org.name)
    if request.method == 'POST':
        form = MemberSignupForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            up = UserProfile.objects.get(user=user)
            messages.success(request, _("""Welcome %s %s.
                                        Your account %s was created with
                                        the username %s""" % (user.first_name, user.last_name,
                                                              up.subject, user.username)))

            if user.is_active:
                messages.success(request, _(
                    "Your account is active and you may log in."))
            else:
                messages.error(request, _(
                    "Your account is not active so you may not log in at this time."))

                messages.warning(request, _(
                    """Someone at %s needs to activate your account.""" % (org.name, )))

            if user.email:
                messages.info(request, _(
                    "Check your email to confirm your email address."))
            else:
                messages.warning(request, _("""You did not supply an email.
                                            For your security, please consider
                                            adding an email to this account."""))

            if up.mobile_phone_number:
                messages.info(request, _(
                    "Thanks for providing a mobile phone number. A welcome message is on the way."))
            else:
                messages.warning(request, _("""You did not supply a mobile phone number.
                                            So we may contact you, please consider
                                                 adding a mobile phone number to this account."""))

            msg = _("""As a reminder, you created this
                    account to gain access to <a href="%s">%s</a>.""" % (settings.KILLER_APP_URI,
                                                                         settings.KILLER_APP_TITLE))

            messages.info(request, _(mark_safe(msg)))

            # Notify Org member to approve ID.

            return HttpResponseRedirect(reverse('home'))
        else:
            # return the bound form with errors
            messages.error(request, _("The form contained errors."))
            return render(request,
                          'generic/bootstrapform.html',
                          {'name': name, 'form': form,
                           'org_slug': org.slug,
                           'domain': org.domain,
                           'service_title': service_title})
    else:
        # this is an HTTP  GET
        # Adding ability to pre-fill invitation_code and email
        # via GET parameters
        form_data = {
            'invitation_code': request.GET.get('invitation_code', ''),
            'email': request.GET.get('email', ''),
            'first_name': request.GET.get('first_name', ''),
            'last_name': request.GET.get('last_name', ''),
            'nickname': request.GET.get('nickname', ''),
            'sex': request.GET.get('sex', ''),
            'gender': request.GET.get('gender', ''),
            'phone_number': request.GET.get('phone_number', ''),
            'org_slug': org.slug}
        return render(request, 'generic/bootstrapform.html',
                      {'name': name, 'form':
                       MemberSignupForm(initial=form_data),
                       'service_title': service_title})
