
import logging
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _
from .models import IndividualIdentifier, UserProfile
from django.http import Http404
from .identifier_forms import IndividualIdentifierForm


def add_identifiers(request, subject):
    up = get_object_or_404(UserProfile, subject=subject)

    request.GET.get()
    IndividualIdentifier.objects.create()

    'type'
    'issuer'
    'value'
    'country'
    'subdivision'
    'uri'
