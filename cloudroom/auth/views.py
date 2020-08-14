from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout
from django.core.exceptions import ObjectDoesNotExist
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.debug import sensitive_post_parameters
from rest_framework import status
from rest_framework.generics import GenericAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenViewBase
from rest_framework_simplejwt.serializers import TokenRefreshSerializer

from .app_settings import (
    JWTSerializer, 
    LoginSerializer,
    UserDetailsSerializer,
)
from .utils import jwt_encode

sensitive_post_parameters_m = method_decorator(
    sensitive_post_parameters(
        'password', 'old_password', 'new_password1', 'new_password2'
    )
)


class TokenCookieRefreshView(TokenViewBase):
    serializer_class = TokenRefreshSerializer

    def post(self, request, *args, **kwargs):
        data = request.data.dict()
        if not data.get('refresh', None):
            data['refresh'] = request.COOKIES.get(
                settings.JWT_AUTH_REFRESH_COOKIE,
                ''
            )
        serializer = self.get_serializer(data=data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        return Response(serializer.validated_data, status=status.HTTP_200_OK)

class LoginView(GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer
    throttle_scope = 'dj_rest_auth'

    @sensitive_post_parameters_m
    def dispatch(self, *args, **kwargs):
        return super(LoginView, self).dispatch(*args, **kwargs)

    def process_login(self):
        django_login(self.request, self.user)

    def get_response_serializer(self):
        return JWTSerializer

    def login(self):
        self.user = self.serializer.validated_data['user']
        self.access_token, self.refresh_token = jwt_encode(self.user)

        if getattr(settings, 'REST_SESSION_LOGIN', True): self.process_login()

    def set_auth_cookie(self, response):
        from datetime import datetime
        from rest_framework_simplejwt.settings import api_settings as jwt_stgs
        response.set_cookie(
            settings.JWT_AUTH_REFRESH_COOKIE,
            self.refresh_token,
            expires=(datetime.utcnow() + jwt_stgs.REFRESH_TOKEN_LIFETIME),
            secure=False,
            httponly=True,
            samesite='Lax'
        )

    def get_response(self):
        serializer_class = self.get_response_serializer()

        data = {
            'user': self.user,
            'access_token': self.access_token,
            'refresh_token': self.refresh_token
        }
        serializer = serializer_class(
            instance=data,
            context=self.get_serializer_context()
        )

        response = Response(serializer.data, status=status.HTTP_200_OK)
        self.set_auth_cookie(response)
        return response

    def post(self, request, *args, **kwargs):
        self.request = request
        self.serializer = self.get_serializer(data=self.request.data)
        self.serializer.is_valid(raise_exception=True)

        self.login()
        return self.get_response()

class LogoutView(APIView):
    """
    Calls Django logout method and delete the Token object
    assigned to the current User object.

    Accepts/Returns nothing.
    """
    permission_classes = (AllowAny,)
    throttle_scope = 'dj_rest_auth'

    def get(self, request, *args, **kwargs):
        if getattr(settings, 'ACCOUNT_LOGOUT_ON_GET', False):
            response = self.logout(request)
        else:
            response = self.http_method_not_allowed(request, *args, **kwargs)

        return self.finalize_response(request, response, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.logout(request)

    def logout(self, request):
        try:
            request.user.auth_token.delete()
        except (AttributeError, ObjectDoesNotExist):
            pass

        if getattr(settings, 'REST_SESSION_LOGIN', True): django_logout(request)

        response = Response(
            {"detail": _("Successfully logged out.")},
            status=status.HTTP_200_OK
        )

        cookie_name = getattr(settings, 'JWT_AUTH_REFRESH_COOKIE', None)
        if cookie_name: response.delete_cookie(cookie_name)
        elif 'rest_framework_simplejwt.token_blacklist' in settings.INSTALLED_APPS:
            # add refresh token to blacklist
            try:
                token = RefreshToken(request.data['refresh'])
                token.blacklist()

            except KeyError:
                response = Response(
                    {"detail": _("Refresh token was not included in request data.")},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            except (TokenError, AttributeError, TypeError) as error:
                if hasattr(error, 'args'):
                    if 'Token is blacklisted' in error.args or 'Token is invalid or expired' in error.args:
                        response = Response({"detail": _(error.args[0])},
                                            status=status.HTTP_401_UNAUTHORIZED)

                    else:
                        response = Response(
                            {"detail": _("An error has occurred.")},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR
                        )

                else:
                    response = Response(
                        {"detail": _("An error has occurred.")},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
        else:
            response = Response(
                {"detail": _(
                    'Neither cookies or blacklist are enabled, '
                    'so the token has not been deleted server side. '
                    'Please make sure the token is deleted client side.'
                )}, 
                status=status.HTTP_200_OK
            )

        return response

class UserDetailsView(RetrieveUpdateAPIView):
    """
    Reads and updates UserModel fields
    Accepts GET, PUT, PATCH methods.

    Default accepted fields: username, first_name, last_name
    Default display fields: pk, username, email, first_name, last_name
    Read-only fields: pk, email

    Returns UserModel fields.
    """
    serializer_class = UserDetailsSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user

    def get_queryset(self):
        """
        Adding this method since it is sometimes called when using
        django-rest-swagger
        """
        return get_user_model().objects.none()
