import math
import random
from rest_framework.pagination import PageNumberPagination

from utils.enums import Enums
from utils.error import APIError, Error


def generate_otp():
    digits = "0123456789"
    OTP = ""
    for i in range(4):
        OTP += digits[math.floor(random.random() * 10)]
    return OTP


def response_data_formating(generalMessage, data, lang=None, error=None):
    response_data = {
        'message': generalMessage,
        'error': error,
        "lang": lang,
        'data': data
    }
    return response_data


def imageResponseObj(data):
    obj = {
        'alt': None,
        'width': None,
        'height': None,
        'url': None
    }
    url = None
    if data.image is not None:
        image = data.image
        if image and hasattr(image, 'url'):
            url = image.url
            if data.__str__() is not None:
                obj['alt'] = data.__str__()

            obj['width'] = image.width
            obj['height'] = image.height
            obj['url'] = url

    return obj


class CustomPageNumberPagination(PageNumberPagination):
    page_size = 10
    allow_empty_first_page = True


def get_language(request):
    lang = request.query_params.get('lang', None)
    if not lang:
        lang = "ar"
    if lang and lang not in ["ar", "en"]:
        raise APIError(Error.DEFAULT_ERROR, extra=["Invalid value for lang parameter. It must be ar or en."])
    
    return lang


def get_stage(user_type):
    if user_type == Enums.FILTERER.value:
        stage = Enums.FILTRATION.value
    elif user_type == Enums.EVALUATOR.value:
        stage = Enums.EVALUATION.value
    elif user_type == Enums.JUDGE.value:
        stage = Enums.JUDGING.value
    else:
        stage = None
    return stage
