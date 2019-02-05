from django import forms
from django.utils.translation import ugettext_lazy as _
from phonenumber_field.formfields import PhoneNumberField
from ..accounts.models import UserProfile


class UserSearchForm(forms.Form):
    first_name = forms.CharField(
        max_length=100, label=_("First Name"), required=False)
    last_name = forms.CharField(
        max_length=100, label=_("Last Name"), required=False)
    username = forms.CharField(
        max_length=30, label=_("User Name"), required=False)
    nickname = forms.CharField(
        max_length=30, label=_("Nickname"), required=False)
    mobile_phone_number = PhoneNumberField(required=False)
    subject = forms.CharField(max_length=16, label=_("Subject"),
                              help_text=_("15 digit account number."), required=False)
    email = forms.EmailField(max_length=150, required=False)
    sex = forms.ChoiceField(initial='',
                            choices=(('', ''), ('F', 'Female'), ('M', 'Male')),
                            required=False)
    birth_date = forms.DateField(required=False)

    required_css_class = 'required'

    def save(self):
        # Get everything from UserProfile.
        query = {}

        first_name = self.cleaned_data.get('first_name').strip().upper()
        if first_name:
            query['user__first_name'] = first_name

        last_name = self.cleaned_data.get('last_name').strip().upper()
        if last_name:
            query['user__last_name'] = last_name

        username = self.cleaned_data.get('username').strip().lower()
        if username:
            query['user__username'] = username

        email = self.cleaned_data.get('email').strip().lower()
        if email:
            query['user__email'] = email
        nickname = self.cleaned_data.get('nickname').strip().upper()
        if nickname:
            query['nickname'] = nickname

        mobile_phone_number = self.cleaned_data.get('mobile_phone_number')
        if mobile_phone_number:
            query['mobile_phone_number'] = mobile_phone_number

        subject = self.cleaned_data.get('subject')
        if subject:
            query['subject'] = subject

        sex = self.cleaned_data.get('sex')
        if sex:
            query['sex'] = sex

        birth_date = self.cleaned_data.get('birth_date')
        if birth_date:
            query['birth_date'] = birth_date

        return UserProfile.objects.filter(**query)


def RepresentsPositiveInt(s, length=10):
    try:
        i = int(s)
        if i > 0 and len(s) == length:
            return True
        return False
    except ValueError:
        return False
