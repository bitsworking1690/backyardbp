"""backyard_backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

# Accounts App Includes #
from accounts.views import RegularTokenObtainPairView, LogoutView, GetTokenDetailsView, CountryListView
from rest_framework_simplejwt.views import TokenRefreshView

# App Permissions #
from rest_framework import permissions

# Swagger App Includes #
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Backyard Platform APIs",
        default_version='v1',
        description="Backyard Platform APIs Endpoints with Request/Response Formats",
        terms_of_service="",
        contact=openapi.Contact(email="waleed@backyardex.com"),
        license=openapi.License(name="BSD License"),
    ),
    permission_classes=[permissions.AllowAny],
    public=True
)

urlpatterns = [
    # Admin (Django)
    path('admin/', admin.site.urls),
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),

    # Custom (Accounts App)
    path('api/auth/token/', RegularTokenObtainPairView.as_view(), name='regular_token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/logout/', LogoutView.as_view(), name='logout'),
    path('api/auth/token/details/', GetTokenDetailsView.as_view(), name='get_token_details'),
    path('api/auth/password-reset/', include('django_rest_passwordreset.urls', namespace='password_reset')),
    path('api/countries/', CountryListView.as_view(), name='country_list'),

    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
