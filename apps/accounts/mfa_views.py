from django.views.generic import TemplateView
from django.views.generic.base import View
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.mfa.backends.sms.backend import SMSBackend
from apps.mfa.backends.sms.models import SMSDevice
from django.http import HttpResponseRedirect
from apps.mfa import verify

# Copyright Videntity Systems Inc.


class EnableSMSMFAView(LoginRequiredMixin, View):
    success_url = "/accounts/mfa"

    def post(self, request, *args, **kwargs):
        user = request.user
        number = user.userprofile.get_verified_phone_number()
        device = SMSDevice.objects.create(
            user=user,
            phone_number=number,
        )
        verify(request, device, backend='apps.mfa.backends.sms.backend.SMSBackend')
        return HttpResponseRedirect(self.success_url)


class DisableSMSMFAView(LoginRequiredMixin, View):
    success_url = "/accounts/mfa"

    def post(self, request, *args, **kwargs):
        user = request.user
        SMSDevice.objects.filter(
            user=user,
        ).delete()
        return HttpResponseRedirect(self.success_url)


class ManageView(LoginRequiredMixin, TemplateView):
    template_name = "mfa.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        context['available'] = self.request.user.userprofile.get_verified_phone_number()
        context['enabled'] = SMSBackend().is_enabled(self.request.user)
        return context
