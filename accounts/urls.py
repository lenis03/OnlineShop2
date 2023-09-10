from django.urls import path

from accounts import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.UserRegisterView.as_view(), name='user_register'),
    path('verify_code/', views.UserVerifyCodeView.as_view(), name='user_verify_code'),
    path('resend_verify_code/', views.UserResendVerifyCodeView.as_view(), name='user_resend_verify_code'),
]
