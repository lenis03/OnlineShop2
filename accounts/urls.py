from django.urls import path

from accounts import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.UserRegisterView.as_view(), name='user_register'),
    path('verify_code/', views.UserRegisterVerifyCodeView.as_view(), name='user_verify_code'),
    path('resend_verify_code/', views.UserRegisterResendVerifyCodeView.as_view(), name='user_resend_verify_code'),
    path('login/', views.UserLoginView.as_view(), name='user_login'),
    path('login_verify_code/', views.UserLoginVerifyCode.as_view(), name='user_login_verify_code'),
    path('login_resend_verify_code/', views.UserLoginResendVerifyCode.as_view(), name='user_login_resend_verify_code'),
    path('logout/', views.UserLogoutView.as_view(), name='user_logout'),

]
