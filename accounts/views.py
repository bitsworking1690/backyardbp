import jwt
from django.conf import settings
from django.db import transaction
from django.middleware import csrf
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from accounts.models import CustomUser, Country
from accounts.permissions import IsOwner, IsAdminOrCRTSupervisor
from accounts.serializers import (
    RegistrationSerializer,
    RegularTokenObtainPairSerializer,
    CheckOTPSerializer,
    ProfileSerializer,
    CountrySerializer,
    CheckAdminOTPSerializer,
    ConfirmOTPSerializer,
    ResponseSerializer,
    ErrorResponseSerializer,
    SignUpResponseSerializer
)
from accounts.services import AccountService
from utils.enums import Enums
from utils.error import APIError, Error
from utils.util import response_data_formating, get_language


class RegularTokenObtainPairView(TokenObtainPairView):
    """ 
    View for obtaining JWTs with enhanced functionality, including OTP email sending for certain user types.
    """

    serializer_class = RegularTokenObtainPairSerializer

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        lang = get_language(request)

        try:
            user = CustomUser.objects.get(email=request.data['email'])
        except CustomUser.DoesNotExist:
            raise APIError(Error.DEFAULT_ERROR, extra=['Email or password is incorrect'])  # noqa

        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            response.set_cookie(
                key=settings.SIMPLE_JWT['AUTH_COOKIE'],
                value=response.data["access"],
                expires=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'],
                secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
                samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE']
            )
        response["X-CSRFToken"] = csrf.get_token(request)

        return self.finalize_response(request, response, *args, **kwargs)
    
    def finalize_response(self, request, response, *args, **kwargs):
        """
        Override the finalize_response method to customize the status code
        """

        if response.status_code == status.HTTP_401_UNAUTHORIZED:
            response.status_code = status.HTTP_400_BAD_REQUEST
        return super().finalize_response(request, response, *args, **kwargs)


class GetTokenDetailsView(APIView):
    """
    View to retrieve details from an authenticated user's JWT token.
    """

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        responses={
            200: openapi.Response("Successful retrieval"),
            401: openapi.Response("Unauthorized")
        }
    )
    def get(self, request):
        try:
            # import pdb
            # pdb.set_trace() n : for next line , c : for exiting the debugger

            jwt_token = request.COOKIES.get("access")
            payload = jwt.decode(jwt_token, settings.SECRET_KEY, algorithms=['HS256'])
            payload['is_profile_completed'] = request.user.is_profile_completed
            payload['first_name'] = request.user.first_name
            payload['email'] = request.user.email
            payload['user_type'] = request.user.user_type
            data = response_data_formating(generalMessage='success', data=payload)
        except Exception as er:
            raise APIError(Error.DEFAULT_ERROR, extra=[f'Invalid or expired token'])  # noqa

        return Response(data=data, status=status.HTTP_200_OK)


class LogoutView(APIView):
    """
    View for logging out an authenticated user, clearing the authentication token cookie.
    """

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        responses={
            200: openapi.Response("Successful logout"),
            401: openapi.Response("Unauthorized")
        }
    )
    def get(self, request):
        try:
            response = Response(response_data_formating(
                generalMessage='success',
                data=["You have been Successfully logged out"])
            )
            response.set_cookie(
                key=settings.SIMPLE_JWT['AUTH_COOKIE'],
                expires='Thu, 01 Jan 1970 00:00:00 GMT',
                secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
                samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE']
            )
            return response
        except Exception as error:
            raise APIError(Error.INVALID_JWT_TOKEN, extra=[f"Invalid token {error}"])  # noqa


class SignUpView(APIView):
    """
    View for user registration, allowing the creation of a new applicant account with validation checks.
    """

    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=RegistrationSerializer,
        responses={
            201: openapi.Response("Successful response", SignUpResponseSerializer),
            400: openapi.Response("Error response", ErrorResponseSerializer)
        },
        manual_parameters=[
            openapi.Parameter(
                name='lang',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                required=False,
                description='The language code for the user interface language ("en", "ar").'
            ),
        ]
    )
    @transaction.atomic
    def post(self, request):
        data = {}
        lang = get_language(request)

        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            AccountService.checkIfEmailAlreadyUsedForCustomUserCreation(data=request.data)
            data = serializer.data
            AccountService.createCustomUser(data, Enums.APPLICANT.value, lang)
            request_status = status.HTTP_201_CREATED
        else:
            request_status = status.HTTP_400_BAD_REQUEST
            raise APIError(Error.DEFAULT_ERROR, extra=[serializer.errors])  # noqa

        return Response(data=response_data_formating(
            generalMessage='success',
            data={"email": data['email']},
            lang=lang),
            status=request_status
        )


class ConfirmEmailOTPView(APIView):
    """
    View for confirming email OTP, allowing validation of the provided OTP.
    """

    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=ConfirmOTPSerializer,
        responses={
            200: openapi.Response("Successful response", ResponseSerializer),
            400: openapi.Response("Error response", ErrorResponseSerializer)
        }
    )
    @transaction.atomic
    def post(self, request):
        data = {}
        serializer = CheckOTPSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.data
            AccountService.validateOTP(data)
            request_status = status.HTTP_200_OK
        else:
            request_status = status.HTTP_400_BAD_REQUEST
            raise APIError(Error.DEFAULT_ERROR, extra=[serializer.errors])  # noqa

        return Response(data=response_data_formating(
            generalMessage='success',
            data=data),
            status=request_status
        )


class ProfileRetrieveUpdateView(APIView):
    """
    View for retrieving and updating user profiles with authentication and ownership checks.
    """

    permission_classes = [IsAuthenticated, IsOwner]

    def get_object(self, pk):
        try:
            return CustomUser.objects.get(pk=pk)
        except CustomUser.DoesNotExist:
            raise APIError(Error.DEFAULT_ERROR, extra=['User not Exist'])  # noqa

    @swagger_auto_schema(
        responses={
            200: openapi.Response("Successful response", ProfileSerializer),
            404: openapi.Response("User not found"),
        }
    )
    def get(self, request, pk):
        user = self.get_object(pk)
        self.check_object_permissions(request, user)
        serializer = ProfileSerializer(user)
        return Response(response_data_formating(
            generalMessage='success',
            data=serializer.data),
            status=status.HTTP_200_OK
        )

    @swagger_auto_schema(
        request_body=ProfileSerializer,
        responses={
            200: openapi.Response("Profile updated successfully"),
            400: openapi.Response("Invalid data"),
        }
    )
    @transaction.atomic
    def put(self, request, pk):
        user = self.get_object(pk)
        self.check_object_permissions(request, user)
        serializer = ProfileSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            AccountService.updateUserProfileStatus(user)
            return Response(response_data_formating(
                generalMessage='success',
                data=serializer.data)
            )
        return Response(response_data_formating(
            generalMessage='error',
            data=None,
            error=serializer.errors),
            status=status.HTTP_400_BAD_REQUEST
        )


class CountryListView(APIView):
    """
    View for retrieving a list of countries with associated cities.
    """

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                name='lang',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                required=False,
                description='The language code for the user interface language (e.g., "en", "ar").'
            )
        ],
        responses={
            200: openapi.Response("Successful response", CountrySerializer),
            400: openapi.Response("Error response", ErrorResponseSerializer),
        }
    )
    def get(self, request):
        lang = get_language(request)

        countries = Country.objects.all()
        serializer = CountrySerializer(countries, many=True, context={'lang': lang})
        return Response(response_data_formating(
            generalMessage='success',
            data=serializer.data,
            lang=lang),
            status=status.HTTP_200_OK
        )


class ConfirmOTPAdminSignInView(APIView):
    """
    View for confirming OTP during admin sign-in, generating and setting authentication tokens.
    """

    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=ConfirmOTPSerializer,
        responses={
            200: openapi.Response("Successful response", ResponseSerializer),
            400: openapi.Response("Error response", ErrorResponseSerializer)
        }
    )
    @transaction.atomic
    def post(self, request):
        data = {}
        serializer = CheckAdminOTPSerializer(data=request.data)

        if serializer.is_valid():
            data = serializer.data
            AccountService.checkAdminExist(data)
            AccountService.verify_admin_otp_email(data)

            try:
                user = CustomUser.objects.get(email=data['email'])
            except CustomUser.DoesNotExist:
                raise APIError(Error.DEFAULT_ERROR, extra=['User not Exist'])  # noqa

            refresh = RefreshToken.for_user(user)
            data['access'] = str(refresh.access_token)
            data['refresh'] = str(refresh)
        else:
            return Response(response_data_formating(
                generalMessage='error',
                error=serializer.errors,
                data=None),
                status=status.HTTP_400_BAD_REQUEST
            )

        response = Response(response_data_formating(
            generalMessage='success',
            data=data),
            status=status.HTTP_200_OK
        )
        response.set_cookie(
            key=settings.SIMPLE_JWT['AUTH_COOKIE'],
            value=data['access'],
            expires=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'],
            secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
            httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
            samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE']
        )
        response["X-CSRFToken"] = csrf.get_token(request)

        return response