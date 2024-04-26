from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from accounts.models import CustomUser
from django.utils.deprecation import MiddlewareMixin
import jwt


class CustomHeaderMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if 'Token_Updated' in request.headers:
            request.META['HTTP_TOKEN_UPDATED'] = False

        raw_token = request.COOKIES.get(
            settings.SIMPLE_JWT['AUTH_COOKIE']) or None

        if raw_token is not None:
            try:
                payload = jwt.decode(
                    raw_token, settings.SECRET_KEY, algorithms=['HS256'])
            except:
                payload = jwt.decode(raw_token, settings.SECRET_KEY, algorithms=[
                                     'HS256'], options={"verify_signature": False})
                user_id = payload['user_id']
                user = CustomUser.objects.get(id=user_id)
                refresh = RefreshToken.for_user(user)

                raw_token_new = refresh.access_token
                raw_token_new['first_name'] = user.first_name
                raw_token_new['last_name'] = user.last_name
                raw_token_new['email_address'] = user.email
                raw_token_new['user_type'] = user.user_type

                new_payload = jwt.decode(
                    str(raw_token_new), settings.SECRET_KEY, algorithms=['HS256'])

                request.COOKIES[settings.SIMPLE_JWT['AUTH_COOKIE']] = str(
                    raw_token_new)
                request.META['HTTP_TOKEN_UPDATED'] = True


class CustomAssingCookieMiddleware:

    def getRequestHeaders(self, string, request):
        if request.headers:
            if string in request.headers:
                return request.headers[string]
            else:
                return False
        else:
            return False

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        updated = self.getRequestHeaders('Token_Updated', request)
        if updated:
            access = request.COOKIES['access']

            response.set_cookie(
                key=settings.SIMPLE_JWT['AUTH_COOKIE'],
                value=access,
                expires=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'],
                secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
                samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE']
            )

        return response
