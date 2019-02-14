from django.contrib.auth.mixins import LoginRequiredMixin
from django import forms
from django.views.generic import (
    CreateView,
)

from oauth2_provider.models import get_application_model


class ApplicationForm(forms.ModelForm):
    client_type = forms.CharField(initial="confidential", disabled=True)
    authorization_grant_type = forms.CharField(initial="authorization-code", disabled=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['client_id'].disabled = True
        self.fields['client_secret'].disabled = True

    class Meta:
        model = get_application_model()
        fields = (
            "name", "client_id", "client_secret", "client_type",
            "authorization_grant_type", "redirect_uris"
        )


class ApplicationRegistration(LoginRequiredMixin, CreateView):
    template_name = "oauth2_provider/application_registration_form.html"
    form_class = ApplicationForm

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)
