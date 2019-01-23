from django.views.generic.edit import FormView
from django.utils import timezone
from django import forms
from apps.mfa import verify
from .models import SMSCode
from django.contrib.auth.mixins import LoginRequiredMixin


class CodeForm(forms.Form):
    code = forms.CharField()

    def clean_code(self):
        data = self.cleaned_data['code']
        if not SMSCode.objects.filter(
            code=data,
            device__user=self.request.user,
            expires__gt=timezone.now(),
        ).exists():
            raise forms.ValidationError("Incorrect code!")

        # Always return a value to use as the new cleaned data, even if
        # this method didn't change it.
        return data


class CodeView(LoginRequiredMixin, FormView):
    template_name = 'code.html'
    form_class = CodeForm
    success_url = '/'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.request = self.request
        return form

    def form_valid(self, form):
        data = form.cleaned_data['code']
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        device = SMSCode.objects.get(
            code=data,
            device__user=self.request.user,
            expires__gt=timezone.now()).device

        verify(self.request, device)
        return super().form_valid(form)
