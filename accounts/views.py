from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.utils import timezone
from datetime import timedelta
import random
from utils import send_otp_code
from django.contrib import messages

from accounts.forms import UserRegisterForm, VerifyCodeForm
from accounts.models import OtpCode, CustomUser


class UserRegisterView(View):
    form_class = UserRegisterForm
    template_name = 'accounts/register.html'

    def get(self, request):
        form = self.form_class
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            random_code = random.randint(100000, 999999)
            send_otp_code(str(cd['phone_number']), random_code)
            OtpCode.objects.create(phone_number=cd['phone_number'], code=random_code)
            request.session['user_registration_info'] = {
                'phone_number': str(cd['phone_number']),
                'email': cd['email'],
                'user_name': cd['user_name'],
                'first_name': cd['first_name'],
                'last_name': cd['last_name'],
                'password': cd['password1'],
            }
            messages.success(request, 'We send you a verify code!', 'success')
            return redirect('accounts:user_verify_code')
        return render(request, self.template_name, {'form': form})


class UserVerifyCodeView(View):
    form_class = VerifyCodeForm
    template_name = 'accounts/verify.html'

    def get(self, request):
        form = self.form_class
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if 'user_registration_info' in request.session:
            user_session = request.session['user_registration_info']
        else:
            messages.error(request, 'First complete registration form', 'danger')
            return redirect('accounts:user_register')

        otp_code_instance = get_object_or_404(OtpCode, phone_number=user_session['phone_number'])
        if form.is_valid():
            cd = form.cleaned_data
            if cd['code'] == otp_code_instance.code:
                current_time = timezone.now()
                code_expiration_time = otp_code_instance.created + timedelta(minutes=2)
                if current_time <= code_expiration_time:
                    CustomUser.objects.create_user(
                        user_session['phone_number'],
                        user_session['email'],
                        user_session['user_name'],
                        user_session['first_name'],
                        user_session['last_name'],
                        user_session['password']
                    )
                    otp_code_instance.delete()
                    del request.session['user_registration_info']
                    messages.success(request, 'You registered successfully.', 'success')
                    return redirect('home:home')
                else:
                    messages.error(request, 'This code has expired', 'danger')
                    return redirect('accounts:user_verify_code')
            else:
                messages.error(request, 'This code is wrong!', 'danger')
                return redirect('accounts:user_verify_code')
        return render(request, self.template_name, {'form': form})


class UserResendVerifyCodeView(View):
    def get(self, request):
        if 'user_registration_info' in request.session:
            user_session = request.session['user_registration_info']
            phone_number = user_session['phone_number']
            existing_code = OtpCode.objects.filter(phone_number=phone_number).first()
            if existing_code:
                current_time = timezone.now()
                code_expiration_time = existing_code.created + timedelta(minutes=2)
                if current_time >= code_expiration_time:
                    existing_code.delete()
                    randon_code = random.randint(100000, 999999)
                    OtpCode.objects.create(phone_number=phone_number, code=randon_code)
                    send_otp_code(phone_number, randon_code)
                    messages.success(request, 'A new code has been send to your phone', 'success')
                    return redirect('accounts:user_verify_code')
                else:
                    messages.error(request, 'A valid code already exists for this phone number!', 'danger')
                    return redirect('accounts:user_verify_code')
            else:
                randon_code = random.randint(100000, 999999)
                OtpCode.objects.create(phone_number=phone_number, code=randon_code)
                send_otp_code(phone_number, randon_code)
                messages.success(request, 'A new code has been send to your phone', 'success')
                return redirect('accounts:user_verify_code')

        else:
            messages.error(request, 'First complete registration form', 'danger')
            return redirect('accounts:user_register')


