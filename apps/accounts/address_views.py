import logging
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from .models import Address, UserProfile
from django.http import Http404
from .address_forms import AddressForm

# Copyright Videntity Systems Inc.

logger = logging.getLogger('verifymyidentity_.%s' % __name__)


@login_required
def display_addresses(request, subject=None):
    name = _('Addresses')

    if not subject:
        # Looking at your own record.
        user = request.user
        up = get_object_or_404(UserProfile, user=user)
    else:
        up = get_object_or_404(UserProfile, subject=subject)
        # Check permission that the user can view other profiles.
        if not request.user.has_perm('accounts.view_address') and up.user != request.user:
            raise Http404()
        user = up.user
    addresses = Address.objects.filter(user=user)
    context = {'user': user, 'addresses': addresses, 'up': up, 'name': name}
    return render(request, 'addresses-table.html', context)


@login_required
def add_new_address(request, subject):
    name = _('Add a New Address')
    up = get_object_or_404(UserProfile, subject=subject)
    # Check permission that the user can view other profiles.
    if not request.user.has_perm('accounts.add_address') and up.user != request.user:
        raise Http404()
    user = up.user
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            a = form.save(commit=False)
            a.user = user
            a.save()
            messages.success(request, 'Address added.')
            return HttpResponseRedirect(reverse('display_addresses_subject', args=(up.subject,)))
        else:
            return render(request, 'generic/bootstrapform.html', {'form': form, 'name': name})

    context = {'name': name, 'user': user,  'up': up,
               'form': AddressForm()}
    return render(request, 'generic/bootstrapform.html', context)


@login_required
def edit_address(request, id):
    name = _('Edit Address')
    address = get_object_or_404(Address, id=id)
    # Check permission that the user can view other profiles.
    if not request.user.has_perm('accounts.change_address') and address.user != request.user:
        raise Http404()

    up = get_object_or_404(UserProfile, user=address.user)
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save(commit=True)
            messages.success(request, 'Address edited.')
            return HttpResponseRedirect(reverse('display_addresses_subject', args=(up.subject,)))
        else:
            return render(request, 'generic/bootstrapform.html', {'form': form, 'name': name})

    context = {'name': name, 'user': address.user,  'up': up,
               'form': AddressForm(instance=address)}
    return render(request, 'generic/bootstrapform.html', context)


@login_required
def delete_address(request, id):
    address = Address.objects.get(id=id)
    # Check permission that the user can view other profiles.
    if not request.user.has_perm('accounts.delete_address') and address.user != request.user:
        raise Http404()
    up = get_object_or_404(UserProfile, user=address.user)
    address.delete()

    messages.success(request, 'Address deleted.')
    return HttpResponseRedirect(reverse('display_addresses_subject', args=(up.subject,)))
