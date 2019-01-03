
from django import forms
from .models import Address

# Copyright Videntity Systems Inc.


class AddressForm(forms.ModelForm):

    class Meta:
        model = Address
        fields = ['street_1', 'street_2', 'city', 'state', 'zipcode']
