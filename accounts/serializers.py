from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from accounts.models import CustomUser, City, Country
from utils.util import response_data_formating
from utils.validators import custom_password_validator


class RegularTokenObtainPairSerializer(TokenObtainPairSerializer):
    default_error_messages = {
        "no_active_account": response_data_formating(
            generalMessage='error',
            data=None,
            lang=None,
            error=['Email or password is incorrect']
        )
    }

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['first_name'] = user.first_name
        token['email'] = user.email
        token['user_type'] = user.user_type
        return token


class RegistrationSerializer(serializers.Serializer):
    email = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    phone_number = serializers.CharField(required=True)

    def validate(self, data):
        """
        # validate Password
            - Email not the same as password
            - Pssword pass the regex
            - password and confirm Password must be match
        """
        if data['email'] == data['password']:
            raise serializers.ValidationError(
                "Password can not be same as email")
        if not custom_password_validator(data['password']):
            raise serializers.ValidationError(
                "Length must be between 8 to 15 characters, should not contain more than 3 "
                "repeated characters consecutively, and at least contains one uppercase, lowercase and special "
                "characters.")
        if data['confirm_password'] != data['password']:
            raise serializers.ValidationError("Passwords are not Matching")
        return data


class CheckOTPSerializer(serializers.Serializer):
    otp = serializers.CharField(required=True)
    email = serializers.CharField(required=True)


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'first_name', 'last_name', 'phone_number',
                  'user_type', 'profile_image', 'dob', 'gender', 'country', 'city', 'education_level',
                  'platform_source']
        read_only_fields = ['email', 'user_type']


class CitySerializer(serializers.ModelSerializer):

    def __init__(self, *args, **kwargs):
        lang = kwargs.get("context", {}).get("lang")
        super().__init__(*args, **kwargs)

        exclude_fields = ['en_name']
        if lang == 'en':
            exclude_fields = ['ar_name']

        for field_name in exclude_fields:
            self.fields.pop(field_name, None)

    class Meta:
        model = City
        fields = ['id', 'en_name', 'ar_name']


class CountrySerializer(serializers.ModelSerializer):
    cities = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        lang = kwargs.get("context", {}).get("lang")
        super().__init__(*args, **kwargs)

        exclude_fields = ['en_name']
        if lang == 'en':
            exclude_fields = ['ar_name']

        for field_name in exclude_fields:
            self.fields.pop(field_name, None)

    def get_cities(self, obj):
        lang = self.context.get('lang')
        cities = City.objects.filter(country=obj)
        cities = CitySerializer(cities, many=True, context={'lang': lang})
        return cities.data

    class Meta:
        model = Country
        fields = ['id', 'en_name', 'ar_name', 'cities']


class CheckAdminOTPSerializer(serializers.Serializer):
    otp = serializers.CharField(required=True)
    email = serializers.CharField(required=True)


class ConfirmOTPSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    otp = serializers.CharField(required=True)


class ResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()


class ErrorResponseSerializer(serializers.Serializer):
    error = serializers.DictField()


class SignUpResponseSerializer(serializers.Serializer):
    email = serializers.EmailField()
