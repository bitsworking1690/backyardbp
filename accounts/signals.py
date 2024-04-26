from django_rest_passwordreset.signals import reset_password_token_created
from django.dispatch import receiver
from django.conf import settings
from django.contrib.auth.signals import user_logged_in
from django.db.models.signals import pre_delete
from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
from django.utils import timezone

from utils.email import reset_password_email
from utils.util import get_language
import redis


# redis_client = redis.StrictRedis(
#     host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)


@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    """
    Signal handler for the creation of a reset password token, triggers an email with a reset password link.
    """

    lang = get_language(instance.request)
    frontend_url = settings.FRONTEND_SITE_URL
    reset_password_url = f"{frontend_url}/reset-password/?token={reset_password_token.key}"    
    reset_password_email(reset_password_url, reset_password_token.user.first_name, reset_password_token.user.email, lang)


# @receiver(user_logged_in)
# def clear_failed_login_attempts(sender, user, request, **kwargs):
#     """
#     Signal handler for clearing failed login attempts upon successful user login.
#     """

#     email = user.email
#     key = f'failed_login_attempts:{email}'
#     redis_client.delete(key)


@receiver(pre_delete, sender=get_user_model())
def user_pre_delete(sender, instance, **kwargs):
    sessions = Session.objects.filter(expire_date__gte=timezone.now())
    for session in sessions:
        session_data = session.get_decoded()
        if str(instance.id) == session_data.get('_auth_user_id'):
            session.delete()
