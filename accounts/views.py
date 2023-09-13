from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.utils import timezone
from datetime import timedelta
import random
from utils import send_otp_code
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth import authenticate
from django.contrib.auth.mixins import LoginRequiredMixin

from accounts.forms import UserRegisterForm, VerifyCodeForm, UserLoginForm
from accounts.models import OtpCode, CustomUser


class UserRegisterView(View):
    form_class = UserRegisterForm
    template_name = 'accounts/register.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.success(request, 'You\'re loging Now')
            return redirect('home:home')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = self.form_class
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            random_code = random.randint(100000, 999999)
            OtpCode.objects.create(phone_number=cd['phone_number'], code=random_code)
            send_otp_code(str(cd['phone_number']), random_code)
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


class UserRegisterVerifyCodeView(View):
    form_class = VerifyCodeForm
    template_name = 'accounts/verify.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.success(request, 'You\'re loging Now')
            return redirect('home:home')
        return super().dispatch(request, *args, **kwargs)

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

        otp_code_instance = OtpCode.objects.filter(phone_number=user_session['phone_number']).last()
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
                    return redirect('accounts:user_login')
                else:
                    messages.error(request, 'This code has expired', 'danger')
                    return redirect('accounts:user_verify_code')
            else:
                messages.error(request, 'This code is wrong!', 'danger')
                return redirect('accounts:user_verify_code')
        return render(request, self.template_name, {'form': form})


class UserRegisterResendVerifyCodeView(View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.success(request, 'You\'re loging Now')
            return redirect('home:home')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        if 'user_registration_info' in request.session:
            user_session = request.session['user_registration_info']
            phone_number = user_session['phone_number']
            existing_code = OtpCode.objects.filter(phone_number=phone_number).last()
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


class UserLoginView(View):
    form_class = UserLoginForm
    template_name = 'accounts/login.html'

    def setup(self, request, *args, **kwargs):
        self.next = request.GET.get('next')
        return super().setup(request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.success(request, 'You\'re loging Now')
            return redirect('home:home')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = self.form_class
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            phone_email = cd['phone_email']
            user = authenticate(
                request=request,
                phone_email=phone_email,
                password=cd['password'],
            )
            if user is not None:
                random_code = random.randint(100000, 999999)
                if '@' in phone_email:
                    user_instance = get_object_or_404(CustomUser, email=str(phone_email))
                    OtpCode.objects.create(phone_number=user_instance.phone_number, code=random_code)
                    send_otp_code(str(user_instance.phone_number), random_code)
                    if self.next:
                        request.session['user_login_info'] = {
                            'user_id': user_instance.id,
                            'phone_number': str(user_instance.phone_number),
                            'next': self.next
                        }
                    else:
                        request.session['user_login_info'] = {
                            'user_id': user_instance.id,
                            'phone_number': str(user_instance.phone_number),
                        }

                    messages.success(request, 'We send you a verify code!', 'success')
                    return redirect('accounts:user_login_verify_code')
                else:
                    user_instance = get_object_or_404(CustomUser, phone_number=phone_email)
                    OtpCode.objects.create(phone_number=str(user_instance.phone_number), code=random_code)
                    send_otp_code(str(user_instance.phone_number), random_code)

                    if self.next:
                        request.session['user_login_info'] = {
                            'user_id': user_instance.id,
                            'phone_number': str(user_instance.phone_number),
                            'next': self.next
                        }
                    else:
                        request.session['user_login_info'] = {
                            'user_id': user_instance.id,
                            'phone_number': str(user_instance.phone_number),
                        }
                    messages.success(request, 'We send you a verify code!', 'success')
                    return redirect('accounts:user_login_verify_code')

            else:
                messages.error(request, 'Your (phone number & email address) or password  is incorrect', 'danger')

        return render(request, self.template_name, {'form': form})


class UserLoginVerifyCode(View):
    form_class = VerifyCodeForm
    template_name = 'accounts/login_verify.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.success(request, 'You\'re loging Now')
            return redirect('home:home')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = self.form_class
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if 'user_login_info' in request.session:
            user_session = request.session['user_login_info']
            phone_number = user_session['phone_number']
            otp_pass_instance = OtpCode.objects.filter(phone_number=phone_number).last()
        else:
            messages.error(request, 'First complete user login form!')
            return redirect('accounts:user_login')

        if form.is_valid():
            cd_code = form.cleaned_data['code']
            current_time = timezone.now()
            code_expiration_time = otp_pass_instance.created + timedelta(minutes=2)
            if cd_code == otp_pass_instance.code:
                if current_time <= code_expiration_time:
                    user = get_object_or_404(CustomUser, pk=user_session['user_id'])
                    login(request, user, backend='accounts.backends.PhoneOrEmailAuthenticationBackends')
                    otp_pass_instance.delete()
                    del request.session['user_login_info']
                    messages.success(request, 'You logged in successfully', 'success')
                    if 'next' in user_session:
                        return redirect(user_session['next'])
                    return redirect('home:home')
                else:
                    messages.error(request, 'This code has expired', 'danger')
                    return redirect('accounts:user_login_verify_code')
            else:
                messages.error(request, 'This code is wrong', 'danger')
                return redirect('accounts:user_login_verify_code')

        return render(request, self.template_name, {'form': form})


class UserLoginResendVerifyCode(View):

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.success(request, 'You\'re loging Now')
            return redirect('home:home')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        if 'user_login_info' in request.session:
            user_session = request.session['user_login_info']
            phone_number = user_session['phone_number']
            existing_code = OtpCode.objects.filter(phone_number=phone_number).last()
            random_code = random.randint(100000, 999999)
            if existing_code:
                current_time = timezone.now()
                code_expiration_time = existing_code.created + timedelta(minutes=2)
                if current_time > code_expiration_time:
                    existing_code.delete()
                    random_code = random.randint(100000, 999999)
                    OtpCode.objects.create(phone_number=phone_number, code=random_code)
                    send_otp_code(phone_number=phone_number, code=random_code)
                    messages.success(request, 'A new code has been send to your phone', 'success')
                    return redirect('accounts:user_login_verify_code')
                else:
                    messages.info(request, 'A valid code is already exist for this phone number', 'info')
                    return redirect('accounts:user_login_verify_code')
            else:
                OtpCode.objects.create(phone_number=phone_number, code=random_code)
                send_otp_code(phone_number=phone_number, code=random_code)
                messages.success(request, 'A new code has been send to your phone', 'success')
                return redirect('accounts:user_login_verify_code')
        else:
            messages.error(request, 'First complete login form', 'danger')
            return redirect('accounts:user_login')


class UserLogoutView(LoginRequiredMixin, View):
    def get(self, request):
        logout(request)
        messages.success(request, 'You logged out successfully', 'success')
        return redirect('home:home')
