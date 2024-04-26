from enum import Enum


class Enums(Enum):

    # USERS_ROLES_CHOICES
    ADMIN = 1
    APPLICANT = 2
    CRT_SUPERVISOR = 3
    CRT_STAFF = 4
    FILTERER = 5        #Evaluator
    EVALUATOR = 6       #Evaluator
    JUDGE = 7
    MOC_STAFF = 8
    PRIO_EVALUATOR = 9  #Evaluator
    PRIO_JUDGE = 10     #Evaluator

    # GENDER_CHOICES
    MALE = 1
    FEMALE = 2

    # OTP_STAGES
    SIGN_UP = 1
    ADMIN_LOGIN = 2

    # STATUS_CHOICES
    ACTIVE = 1
    INACTIVE = 2