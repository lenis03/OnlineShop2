from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.widgets import PhoneNumberPrefixWidget

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


class UserRegisterForm(forms.Form):
    phone_number = PhoneNumberField(region="IR", label='Phone Number', widget=PhoneNumberPrefixWidget(
            country_choices=[
                 ("IR", "Iran"),

            ],
        ),
    )
    email = forms.EmailField(label='Email')
    user_name = forms.CharField(label='UserName')
    first_name = forms.CharField(label='FirstName')
    last_name = forms.CharField(label='LastName')
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='ConfirmPassword', widget=forms.PasswordInput)

    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']
        custom_user = CustomUser.objects.filter(phone_number=phone_number).exists()
        if custom_user:
            raise ValidationError('This phone number is already exists!')
        return phone_number

    def clean_email(self):
        email = self.cleaned_data['email']
        custom_user = CustomUser.objects.filter(email=email).exists()
        if custom_user:
            raise ValidationError('This email address is already exists!')
        return email

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password1'] and cd['password2'] and cd['password1'] != cd['password2']:
            raise ValidationError('password don\'t match ')


class VerifyCodeForm(forms.Form):
    code = forms.IntegerField()
