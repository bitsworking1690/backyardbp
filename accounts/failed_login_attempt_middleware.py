from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.utils import timezone
from rest_framework import status
from utils.enums import Enums
from utils.util import response_data_formating
from accounts.models import FailedLoginAttempts
from datetime import timedelta
import redis


class FailedLoginAttemptMiddleware:
    """
    Middleware to track and handle failed login attempts, blocking users temporarily after reaching the maximum allowed attempts.
    """

    def __init__(self, get_response):
        """
        Initialize the middleware.
        """

        self.get_response = get_response
        self.redis_client = redis.StrictRedis(
            host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)

    def __call__(self, request):
        """
        Handle the incoming request and check for failed login attempts.
        """

        response_to_return = None
        if request.method == 'POST' and request.path == '/api/auth/token/':
            email = request.POST.get('email')
            password = request.POST.get('password')
            user = get_user_model()
            if email and password:
                user = user.objects.filter(email=email).first()
                if user:
                    is_password_true = user.check_password(password)
                    if not is_password_true:
                        response_to_return = self.check_and_increment_failed_login_attempts(
                            email, user.user_type, user)
                    elif is_password_true:
                        key = f'failed_login_attempts:{email}'
                        current_attempts = int(self.redis_client.get(key) or 0)
                        if current_attempts >= int(settings.MAX_FAILED_LOGIN_ATTEMPTS):
                            return self.create_response()
        response = self.get_response(request)
        return response_to_return or response

    def check_and_increment_failed_login_attempts(self, email, user_type, user):
        """
        Check and increment failed login attempts for applicants.
        """

        if user_type == Enums.APPLICANT.value:
            key = f'failed_login_attempts:{email}'
            current_attempts = int(self.redis_client.get(key) or 0)
            if current_attempts >= int(settings.MAX_FAILED_LOGIN_ATTEMPTS):
                self.block_user(user)
                return self.create_response()
            else:
                if not current_attempts:
                    self.redis_client.setex(
                        key, settings.FAILED_LOGIN_ATTEMPT_TTL, 1)
                else:
                    self.redis_client.incr(key)

    def create_response(self):
        """
        Create a JSON response for blocking users temporarily.
        """

        return JsonResponse(
            response_data_formating(
                generalMessage='error', data=None, lang=None, 
                error=['You have exceeded the maximum allowed attempts, your account is blocked temporarily, try again after some time']
            ),
            status=status.HTTP_400_BAD_REQUEST
        )

    def block_user(self, user):
        """
        Block the user temporarily and record the failed login attempt.
        """
        
        ttl_seconds = int(settings.FAILED_LOGIN_ATTEMPT_TTL)
        start_time = timezone.now() - timedelta(seconds=ttl_seconds)
        end_time = timezone.now()

        failed_login_attempt = FailedLoginAttempts.objects.filter(
            user=user, created_at__range=(start_time, end_time)).first()
        
        if not failed_login_attempt:
            FailedLoginAttempts.objects.create(user=user)
