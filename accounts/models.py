from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from utils.validators import validate_file_size_image
from django.contrib.auth.base_user import BaseUserManager
from utils.enums import Enums
from utils.models import BaseModel
from django.core.validators import FileExtensionValidator


USER_TYPE_CHOICES = (
    (Enums.ADMIN.value, 'Admin'),
    (Enums.APPLICANT.value, 'Applicant'),
    (Enums.CRT_SUPERVISOR.value, 'CRT Supervisor'),
    (Enums.CRT_STAFF.value, 'CRT Staff'),
    (Enums.FILTERER.value, 'Filterer'),
    (Enums.EVALUATOR.value, 'Evaluator'),
    (Enums.JUDGE.value, 'Judge'),
    (Enums.MOC_STAFF.value, 'MoC Staff'),
    (Enums.PRIO_EVALUATOR.value, 'Prio Evaluator'),
    (Enums.PRIO_JUDGE.value, 'Prio Judge'),
)

USER_GENDER_CHOICES = (
    (Enums.MALE.value, 'Male'),
    (Enums.FEMALE.value, 'Female')
)


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('user_type', 1)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    phone_number = models.CharField(('Mobile Number'), max_length=14, null=True, blank=True)
    user_type = models.PositiveSmallIntegerField(choices=USER_TYPE_CHOICES, default=2)
    first_name = models.CharField(max_length=256)
    last_name = models.CharField(max_length=256)
    profile_image = models.ImageField(upload_to='profile_image/', validators=[FileExtensionValidator(
        allowed_extensions=['png', 'jpg', 'jpeg'],), validate_file_size_image], null=True, blank=True)
    dob = models.DateField(verbose_name=_("Date of Birth"), null=True, blank=True)
    country = models.ForeignKey('Country', on_delete=models.SET_NULL, null=True, blank=True)
    city = models.ForeignKey('City', on_delete=models.SET_NULL, null=True, blank=True)
    gender = models.PositiveSmallIntegerField(choices=USER_GENDER_CHOICES, null=True, blank=True)
    is_profile_completed = models.BooleanField(default=False, null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = UserManager()

    class Meta:
        ordering = ('id',)

    def __str__(self):
        return f"{self.email} - {self.id}"

    def save(self, *args, **kwargs):
        self.email = self.email.lower()
        return super().save(*args, **kwargs)


class Country(BaseModel):
    en_name = models.CharField(max_length=256)
    ar_name = models.CharField(max_length=256)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.en_name


class City(BaseModel):
    en_name = models.CharField(max_length=256)
    ar_name = models.CharField(max_length=256)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.en_name


class EmailOtp(BaseModel):
    OTP_STAGES = (
        (Enums.SIGN_UP.value, 'Sign Up'),
        (Enums.ADMIN_LOGIN.value, 'Admin Login')
    )

    email = models.EmailField()
    otp = models.CharField(max_length=4)
    is_valid = models.BooleanField(default=True)
    stage = models.PositiveSmallIntegerField(choices=OTP_STAGES, default=1)

    class Meta:
        ordering = ['-id']

    def save(self, *args, **kwargs):
        self.email = self.email.lower()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.otp


class FailedLoginAttempts(BaseModel):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-id']
