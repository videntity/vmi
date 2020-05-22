import logging
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from .models import IndividualIdentifier, UserProfile
from django.http import Http404
from .identifier_forms import IndividualIdentifierForm

# Copyright Videntity Systems Inc.

logger = logging.getLogger('verifymyidentity_.%s' % __name__)


@login_required
def display_individual_identifiers(request, subject=None):
    name = _('Identifiers')
    if not subject:
        # Looking at your own record.
        user = request.user
        up = get_object_or_404(UserProfile, user=user)
    else:
        up = get_object_or_404(UserProfile, subject=subject)
        # Check permission that the user can view other profiles.
        if not request.user.has_perm('accounts.view_individualidentifier') and up.user != request.user:
            raise Http404()
        user = up.user
    identifiers = IndividualIdentifier.objects.filter(user=user)
    context = {'user': user, 'identifiers': identifiers,
               'up': up, 'name': name}
    return render(request, 'identifiers-table.html', context)


@login_required
def add_new_individual_identifier(request, subject):
    name = _('Add a New Identifier')
    up = get_object_or_404(UserProfile, subject=subject)
    # Check permission that the user can view other profiles.
    if not request.user.has_perm('accounts.add_individualidentifier') and up.user != request.user:
        raise Http404()
    user = up.user
    if request.method == 'POST':
        form = IndividualIdentifierForm(request.POST)
        if form.is_valid():
            ii = form.save(commit=False)
            ii.user = user
            ii.save()
            messages.success(request, 'Identifier added.')
            return HttpResponseRedirect(reverse('display_individual_identifiers_subject', args=(up.subject,)))
        else:
            return render(request, 'generic/bootstrapform.html', {'form': form, 'name': name})

    context = {'name': name, 'user': user,  'up': up,
               'form': IndividualIdentifierForm()}
    return render(request, 'generic/bootstrapform.html', context)


@login_required
def edit_individual_identifier(request, id):
    name = _('Edit Identifier')
    identifier = get_object_or_404(IndividualIdentifier, id=id)
    # Check permission that the user can view other profiles.
    if not request.user.has_perm('accounts.change_individualidentifier') and identifier.user != request.user:
        raise Http404()

    identifier = get_object_or_404(IndividualIdentifier, id=id)
    up = get_object_or_404(UserProfile, user=identifier.user)
    if request.method == 'POST':
        form = IndividualIdentifierForm(request.POST, instance=identifier)
        if form.is_valid():
            form.save()
            messages.success(request, 'Identifier edited.')
            return HttpResponseRedirect(reverse('display_individual_identifiers_subject', args=(up.subject,)))
        else:
            return render(request, 'generic/bootstrapform.html', {'form': form, 'name': name})

    context = {'name': name, 'user': identifier.user,  'up': up,
               'form': IndividualIdentifierForm(instance=identifier)}
    return render(request, 'generic/bootstrapform.html', context)


@login_required
def delete_individual_identifier(request, id):
    identifier = IndividualIdentifier.objects.get(id=id)
    # Check permission that the user can view other profiles.
    if not request.user.has_perm('accounts.delete_individualidentifier') and identifier.user != request.user:
        raise Http404()

    up = get_object_or_404(UserProfile, user=identifier.user)
    identifier.delete()

    messages.success(request, 'Identifier deleted.')
    return HttpResponseRedirect(reverse('display_individual_identifiers_subject', args=(up.subject,)))
