from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser, OtpCode


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm

    list_display = (
        'user_name',
        'email',
        'phone_number',
        'is_admin',
        'is_active'
    )
    list_filter = (
        'is_admin',
    )

    fieldsets = (
        ('Main', {'fields': (
            'user_name',
            'email',
            'phone_number',
            'first_name',
            'last_name',
            'password'
        )}),
        ('Permissions', {'fields': (
            'is_admin',
            'is_superuser',
            'is_active',
            'last_login',
            'groups',
            'user_permissions',
        )})

    )

    add_fieldsets = (
        ('AddUser', {'fields': (
            'phone_number',
            'email',
            'user_name',
            'first_name',
            'last_name',
            'password1',
            'password2'
        )}),
    )

    search_fields = ('user_name', 'email')
    ordering = ('user_name', )
    filter_horizontal = ('groups', 'user_permissions')
    readonly_fields = ('last_login', )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        is_superuser = request.user.is_superuser
        if not is_superuser:
            form.base_fields['is_superuser'].disabled = True
        return form


@admin.register(OtpCode)
class OtpCodeAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'code', 'created')

