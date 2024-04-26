from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
import re
from utils.error import Error, APIError


_NAME_REGEX = RegexValidator(
    regex=r"^[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z]+[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z ]*$", message=_("Special characters and digits are now allowed."),
)

_COLLEGE_REGEX = RegexValidator(
    regex=r"^[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z]+[\-\&\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z ]*$", message=_("Digits and special characters (except & and -) are now allowed."),
)

_CARD_HOLDER_NAME_REGEX = RegexValidator(
    regex=r"^((?:[A-Za-z]+ ?){1,6})$", message=_("Special characters and digits are now allowed."),
)

_PHONE_REGEX = RegexValidator(
    regex=r"^\d{9,14}$", message=_("Mobile number must be between 9 and 14 digits and accepts only numbers."),
)


_ID_NUMBER_REGEX = RegexValidator(
    regex=r"\d{10}$", message=_("ID number must be 10 digits."),
)

_CR_NUMBER_REGEX = RegexValidator(
    regex=r"\d{10}$", message=_("Commercial register number must be 10 digits."),
)

_VAT_NUMBER_REGEX = RegexValidator(
    regex=r"\d{15}$", message=_("VAT number must be 15 digits."),
)

_IBAN_REGEX = RegexValidator(
    regex=r"^SA\s*(?:\S\s*){22}$", message=_("IBAN must be in a form of 'SA' followed with 22 digits."),
)


def validate_file_size_image(value):
    max_size = 5 * 1024 * 1024  # 5 MB in bytes
    if value.size > max_size:
        raise ValidationError(
            f"The maximum file size allowed is {max_size/(1024*1024)} MB.")


def validate_file(value):
    max_size = 5 * 1024 * 1024  # 5 MB in bytes
    allowed_extensions = ['pdf']

    if value.size > max_size:
        raise APIError(Error.DEFAULT_ERROR, extra=['The maximum file size allowed is 5 MB']) 

    ext = value.name.split('.')[-1].lower()
    if ext not in allowed_extensions:
        raise APIError(Error.DEFAULT_ERROR, extra=['Only PDF files are allowed']) 


def custom_password_validator(password):

    # Rule 4: Password should be alphanumeric with at least one special character having length b/w 8-15
    regex = r"^(?=.{8,15})(?=.*[a-z])(?=.*[A-Z])(?=.*[{}():;,.?|_`~%/\-*@#$%^&+=!]).*$"
    g = re.compile(regex)

    # Rule 5: Password should not contain more than 3 repeated characters consecutively
    if re.search(r'(.)\1{3,}', password):
        return False
    if re.fullmatch(g, password):
        return True
    return False
