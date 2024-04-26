from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from accounts.models import CustomUser, City, Country, EmailOtp, FailedLoginAttempts
from import_export.admin import ImportExportModelAdmin
from import_export import resources
from django.contrib.auth.hashers import make_password


class UserResource(resources.ModelResource):

    def before_import_row(self, row, **kwargs):
        value = row['password']
        row['password'] = make_password(value)

    class Meta:
        model = CustomUser


@admin.register(CustomUser)
class CustomUserImportExport(UserAdmin, ImportExportModelAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password', 'user_type',)}),
        (('Personal info'), {
         'fields': ('first_name', 'last_name', 'phone_number', 'profile_image', 'dob',
                    'country', 'city', 'gender', 'education_level', 'platform_source', 'is_profile_completed',)}),
        (('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                      'groups', 'user_permissions')}),
        (('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide', ),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name', 'user_type'),
        }),
    )
    list_display = ['id', 'email', 'first_name', 'last_name', 'user_type']
    search_fields = ('email', 'first_name', 'user_type')
    ordering = ('-id',)
    list_filter = [
        'user_type'
    ]

    resource_class = UserResource


@admin.register(Country)
class CountryImportExport(ImportExportModelAdmin):
    list_display = ['id', 'en_name', 'ar_name',
                    'is_active', 'created_at', 'updated_at']
    search_fields = ['en_name']


@admin.register(City)
class CityImportExport(ImportExportModelAdmin):
    list_display = ['id', 'en_name', 'ar_name',
                    'is_active', 'created_at', 'updated_at']
    search_fields = ['en_name']


@admin.register(EmailOtp)
class EmailOtpImportExport(ImportExportModelAdmin):
    list_display = ['id', 'otp', 'email', 'is_valid',
                    'stage', 'is_active', 'created_at', 'updated_at']
    list_filter = ['stage']
    search_fields = ['email']


@admin.register(FailedLoginAttempts)
class FailedLoginAttemptsImportExport(ImportExportModelAdmin):
    list_display = ['id', 'user', 'is_active', 'created_at', 'updated_at']
