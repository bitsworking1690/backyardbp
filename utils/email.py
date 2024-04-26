from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from utils.error import Error, APIError


def otp_email(first_name, email, otp, lang):
    try:
        subject = "OTP Verification"
        
        html_message = render_to_string(
            f'otp_{lang}.html',
            {
                'first_name': first_name,
                'email': email,
                'otp': otp,
                'frontend_url' : settings.FRONTEND_SITE_URL
            }
        )
        plain_message = strip_tags(html_message)
        from_email = settings.EMAIL_HOST_USER
        to = email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=from_email,
            recipient_list=[to],
            html_message=html_message
        )
    except Exception as e:
        raise APIError(Error.DEFAULT_ERROR, extra=[f"Error in Sending Email: {e}"])


def reset_password_email(url, first_name, email, lang):
    try:
        subject = "Reset Password"
        html_message = render_to_string(
            f'reset_password_{lang}.html',
            {
                'first_name': first_name,
                'url': url,
                'frontend_url' : settings.FRONTEND_SITE_URL
            }
        )
        plain_message = strip_tags(html_message)
        from_email = settings.EMAIL_HOST_USER
        to = email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=from_email,
            recipient_list=[to],
            html_message=html_message
        )
    except Exception as e:
        raise APIError(Error.DEFAULT_ERROR, extra=[f"Error in Sending Email: {e}"])


def nomination_others_email(award, first_name, nominated_by, email, lang):
    try:
        subject = "Award Nomination"
        html_message = render_to_string(
            f'nominate_others_{lang}.html',
            {
                'first_name': first_name,
                'nominated_by': nominated_by,
                'award': award,
                'frontend_url' : settings.FRONTEND_SITE_URL
            }
        )
        plain_message = strip_tags(html_message)
        from_email = settings.EMAIL_HOST_USER
        to = email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=from_email,
            recipient_list=[to],
            html_message=html_message
        )
    except Exception as e:
        raise APIError(Error.DEFAULT_ERROR, extra=[f"Error in Sending Email: {e}"])


def nomination_application_confirmation(first_name, email, award, lang):
    try:
        subject = "Nomination Application Confirmation"
        html_message = render_to_string(
            f'nomination_application_success_{lang}.html',
            {
                'first_name': first_name,
                'award': award,
                'frontend_url' : settings.FRONTEND_SITE_URL
            }
        )
        plain_message = strip_tags(html_message)
        from_email = settings.EMAIL_HOST_USER
        to = email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=from_email,
            recipient_list=[to],
            html_message=html_message
        )
    except Exception as e:
        raise APIError(Error.DEFAULT_ERROR, extra=[f"Error in Sending Email: {e}"])
