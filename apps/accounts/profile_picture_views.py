import logging
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
# from .emails import send_new_org_account_approval_email
from django.contrib.auth.decorators import login_required
from .models import UserProfile
from .profile_picture_forms import ProfilePictureForm


# Copyright Videntity Systems Inc.

logger = logging.getLogger('verifymyidentity_.%s' % __name__)


@login_required
def upload_profile_picture(request, subject=None):
    print("subject", subject)
    if not subject:
        # Looking at your own record.
        user = request.user
        up = get_object_or_404(UserProfile, user=user)
    else:
        up = get_object_or_404(UserProfile, subject=subject)
        # Check permission that the user can view other profiles.
        if not request.user.has_perm('accounts.change_userprofile'):
            raise Http404()
        user = up.user
    up = get_object_or_404(UserProfile, user=user)
    name = _("Upload Profile Picture")
    if request.method == 'POST':
        form = ProfilePictureForm(request.POST, request.FILES, instance=up)
        if form.is_valid():

            form.save()
            messages.success(request, _("Profile Picture Updated."))
            return HttpResponseRedirect(reverse('user_profile_subject', args=(up.subject,)))
        else:
            # return the bound form with errors
            return render(request,
                          'generic/bootstrapform.html',
                          {'name': name, 'form': form})
    else:
        # this is an HTTP  GET
        return render(request, 'generic/bootstrapform.html',
                      {'name': name, 'form':
                       ProfilePictureForm(instance=up)})
