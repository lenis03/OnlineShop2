from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from .models import CustomUser


class CustomUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='confirm password', widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ['email', 'phone_number', 'user_name', 'first_name', 'last_name']

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password1'] and cd['password2'] and cd['password1'] != cd['password2']:
            raise ValidationError('passwords don\'t match')
        return cd['password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class CustomUserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField(help_text=
                                         "You can change password using <a href=\"../password/\">this form</a>")

    class Meta:
        model = CustomUser
        fields = [
            'email',
            'phone_number',
            'user_name',
            'first_name',
            'last_name',
            'password',
            'is_admin',
            'is_active',
            'last_login'
        ]
