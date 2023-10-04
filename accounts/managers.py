from django.contrib.auth.models import BaseUserManager


class CustomUserManger(BaseUserManager):
    def create_user(self, phone_number, email, user_name, first_name, last_name, password):
        if not phone_number:
            raise ValueError('user must have phone number!')
        if not email:
            raise ValueError('user must have email!')
        if not user_name:
            raise ValueError('user must have user name!')
        if not first_name:
            raise ValueError('user must have first name!')
        if not last_name:
            raise ValueError('user must have last name!')
        user = self.model(
            phone_number=phone_number,
            email=self.normalize_email(email),
            user_name=user_name,
            first_name=first_name,
            last_name=last_name
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, email, user_name, first_name, last_name, password):
        user = self.create_user(phone_number, email, user_name, first_name, last_name, password)
        user.is_admin = True
        user.is_superuser = True
        user.save(using=self._db)
        return user



