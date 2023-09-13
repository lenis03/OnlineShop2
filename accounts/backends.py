from accounts.models import CustomUser


class PhoneOrEmailAuthenticationBackends:
    @staticmethod
    def authenticate(request, phone_email=None, password=None):
        try:
            if '@' in phone_email:
                user = CustomUser.objects.get(email=phone_email)
                if user and user.check_password(password):
                    return user
                return None
            else:
                user = CustomUser.objects.get(phone_number=phone_email)
                if user and user.check_password(password):
                    return user
                return None
        except CustomUser.DoesNotExist:
            return None

    @staticmethod
    def get_user(user_id):
        try:
            return CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            return None


