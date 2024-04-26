from accounts.models import CustomUser, EmailOtp, Country, City
from utils.error import APIError, Error
from utils.util import generate_otp
from utils.email import otp_email
from utils.enums import Enums
from django.utils.datastructures import MultiValueDictKeyError


class AccountService:
    """
    Service class containing static methods for user account-related operations.
    """

    @staticmethod
    def createCustomUser(data, user_type, lang):
        """
        Create a custom user with the provided data, and send OTP for email verification.
        """

        customUser = CustomUser(
            email=data['email'],
            user_type=user_type,
            is_active=False,
            first_name=data['first_name'],
            last_name=data['last_name'],
            phone_number=data['phone_number']
        )
        customUser.set_password(data['password'])
        customUser.save()

        AccountService.createOTP(data, lang)

    @staticmethod
    def createOTP(data, lang):
        """
        Create and send OTP for email verification.
        """

        otp = EmailOtp(
            email=data['email'],
            otp=generate_otp(),
            is_valid=False
        )
        otp.save()
        otp_email(data['first_name'], data['email'], otp.otp, lang)

    @staticmethod
    def validateOTP(data):
        """
        Validate the OTP and activate the custom user.
        """

        try:
            otp_instance = EmailOtp.objects.get(
                otp=data['otp'], email=data['email'].lower(), is_valid=False, stage=1)
        except EmailOtp.DoesNotExist:
            raise APIError(Error.INSTANCE_NOT_FOUND, extra=[
                           f'Otp Not Found for Provided Email'])

        otp_instance.is_valid = True
        otp_instance.save()

        # Activate Custom User
        try:
            customUser = CustomUser.objects.get(email=data['email'].lower())
        except CustomUser.DoesNotExist:
            raise APIError(Error.INSTANCE_NOT_FOUND,
                           extra=['CustomUser Not Found'])

        customUser.is_active = True
        customUser.save()

    @staticmethod
    def checkIfEmailAlreadyUsedForCustomUserCreation(data):
        """
        Check if the email is already used for custom user creation and handle accordingly.
        """

        if "email" in data:
            if CustomUser.objects.filter(email=data['email'].lower()).exists():
                email_otp = EmailOtp.objects.filter(email=data['email'].lower(), stage=1).first()
                if email_otp:
                    if not email_otp.is_valid:
                        raise APIError(Error.DEFAULT_ERROR, extra=['OTP already sent to your email'])
                raise APIError(Error.DEFAULT_ERROR, extra=['Please Use different Email, Email Already Used'])
        else:
            raise APIError(Error.DEFAULT_ERROR, extra=["Email is Required"])

    @staticmethod
    def updateUserProfileStatus(user):
        """
        Update the user profile status to indicate completion.
        """

        try:
            user = CustomUser.objects.get(id=user.id)
            if not user.is_profile_completed:
                user.is_profile_completed = True
                user.save()
        except CustomUser.DoesNotExist:
            raise APIError(Error.DEFAULT_ERROR, extra=['User not Exist'])

    @staticmethod
    def checkAdminExist(data):
        """
        Check if an admin with the provided email exists.
        """

        if "email" in data:
            user = CustomUser.objects.filter(email=data['email'].lower(), user_type__in=[
                                             Enums.ADMIN.value, Enums.CRT_SUPERVISOR.value, Enums.CRT_STAFF.value, Enums.MOC_STAFF.value,
                                             Enums.FILTERER.value, Enums.EVALUATOR.value, Enums.JUDGE.value, Enums.PRIO_FILTERER.value, 
                                             Enums.PRIO_EVALUATOR.value, Enums.PRIO_JUDGE.value])
            if not user.exists():
                raise APIError(Error.DEFAULT_ERROR, extra=['Admin Role not exist with this Email'])
        else:
            raise APIError(Error.DEFAULT_ERROR, extra=["Email is Required"])

    @staticmethod
    def verify_admin_otp_email(data):
        """
        Verify the admin OTP for email verification.
        """

        try:
            otp_obj = EmailOtp.objects.get(otp=data['otp'], email=data['email'], is_valid=False, stage=2)
        except EmailOtp.DoesNotExist:
            raise APIError(Error.DEFAULT_ERROR, extra=[f'Otp Not Found for Provided Email'])
        otp_obj.is_valid = True
        otp_obj.save()

    @staticmethod
    def sendOTPEmail(user, lang):
        """
        Send OTP email to the user.
        """

        data = {}
        
        email_otp_obj = EmailOtp.objects.filter(email=user.email,is_valid=False, stage=2).first()
        if email_otp_obj:
            otp_email(user.first_name, user.email, email_otp_obj.otp, lang)
        else:
            otp = EmailOtp(
                email=user.email,
                otp=generate_otp(),
                is_valid=False,
                stage=2
            )
            otp.save()
            otp_email(user.first_name, user.email, otp.otp, lang)
        
        data['user_type'] = user.user_type
        data['message'] = "OTP has been sent to your Email"
        
        return data

    @staticmethod
    def update_profile_details(data, crt_form_submission):
        """
        Update user profile details.
        """
        
        user = CustomUser.objects.filter(email=data['email'].lower()).first()

        if user and crt_form_submission == Enums.CRT_FORM_SUBMISSION_ADD:
            raise APIError(Error.INSTANCE_NOT_FOUND, extra=['User already exist with this email']) # noqa

        if not user:
            user = CustomUser()

        user.first_name = data['first_name']
        user.last_name = data['last_name']
        user.gender = data['gender']
        user.phone_number = data['phone_number']
        user.email = data['email']
        user.dob = data['dob']
        try:
            user.country = Country.objects.get(id=data.get('country'))
            user.city = City.objects.get(id=data.get('city')) if data.get('city') else None
        except Country.DoesNotExist:
            raise APIError(Error.DEFAULT_ERROR, extra=['Country not exist with provided id'])
        except MultiValueDictKeyError:
            pass
        user.save()
        user_id = user.id
        return user_id
