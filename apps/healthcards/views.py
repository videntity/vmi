from django.shortcuts import render
from django.contrib.auth import get_user_model
import logging
from .models import SmartHealthCard, SmartHealthJWKS
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from collections import OrderedDict
from django.conf import settings
from django.urls import reverse
from django.shortcuts import render, get_object_or_404, get_list_or_404
from django.contrib.auth.decorators import login_required
from ..accounts.models import UserProfile 
logger = logging.getLogger('smart_health_cards.%s' % __name__)
User = get_user_model()

__author__ = "Alan Viars"

@require_GET
def jwks_json(request):
    """
    Views that returns smart health card /.well-known/jwks.json
    """
    jwks  = get_object_or_404(SmartHealthJWKS, pk=1)
    return JsonResponse(jwks.as_jwks)

@require_GET
@login_required
def display_qr(request):
    pass

@require_GET
@login_required
def display_json(request):
    pass


@require_GET
def display_jws(request):
    pass

@require_GET
@login_required
def display_user_index(request):
    smart_health_cards = SmartHealthCard.objects.filter(user=request.user)
    return render(request, "user_index.html", context={"smart_health_cards": smart_health_cards})


@require_GET
def display_all_shc(request, sub):
    up = get_object_or_404(UserProfile, subject=sub)
    smart_health_cards = get_list_or_404(SmartHealthCard, user=up.user)
    return render(request, "smart_health_cards.html", context={"smart_health_cards": smart_health_cards,
    "profile": up})
