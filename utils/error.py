
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError
from enum import Enum
import logging
logger = logging.getLogger('django')


class Error(Enum):
    DEFAULT_ERROR = {'detail': _('{}')}
    INVALID_JWT_TOKEN = {'detail': _('Invalid token!')}
    INSTANCE_NOT_FOUND = {'detail': _('{}')}
    REQUIRED_FIELD = {'detail':  _('{}')}
    DATA_IS_MISSING = {'detail': _('Data is missing!')}
    NO_ACTIVE_ACCOUNT = {
        'detail': _('No active account found with the given credentials!')}
    PHASE_NOT_FOUND = {
        'detail': _('{} According to application stage, Phase not found!')}
    INVALID_LANG = {'detail': _('Invalid value for lang parameter. It must be ar or en.')}
    INVALID_AWARD = {'detail': _('Invalid value for award_id parameter.')}
    MISSING_AWARD = {'detail': _('award_id parameter is required.')}
    INVALID_CATEGORY = {'detail': _('Invalid value for category_id parameter.')}
    MISSING_CATEGORY = {'detail': _('category_id parameter is required.')}
    MISSING_USER = {'detail': _('Nominee information is required for CRT.')}
    INVALID_NOMINATION = {'detail': _('Invalid value for nomination_id parameter.')}
    MISSING_NOMINATION = {'detail': _('nomination_id does not exist.')}
    NOMINATION_DOES_NOT_EXIST = {'detail': _('Nomination does not exist.')}
    SUBMISSION_DEADLINE_PASSED = {'detail': _('Submission deadline has passed.')}
    AWARD_NOT_ASSIGNED = {'detail': _('Award is not assigned.')}
    MISSING_EVALUATION = {'detail': _('evaluation_id does not exist.')}
    EVALUATION_DOES_NOT_EXIST = {'detail': _('Evaluation does not exist.')}
    EVALUATION_ALREADY_EXIST = {'detail': _('Evaluation already exist.')}
    EVALUATOR_DOES_NOT_EXIST = {'detail': _('Evaluator does not exist.')}
    FORM_ACCEPT_UNCHECKED = {'detail': _('Please acknowledge or check both checkboxes to proceed.')}


class APIError:
    def __init__(self, error: Error, extra=None):
        self.error = error
        self.extra = extra or None
        error_detail = error.value
        if self.extra:
            if isinstance(self.extra, list):
                error_detail['detail'] = {
                    'message': "error",
                    'error': self.extra,
                    'lang': None,
                    'data': None
                }
        try:
            logger.info(error.value)
        except BaseException:
            pass
        raise ValidationError(**error_detail)
