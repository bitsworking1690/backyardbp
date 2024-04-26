from django.urls import path
from accounts.views import (
    SignUpView,
    ConfirmEmailOTPView,
    ProfileRetrieveUpdateView,
    ConfirmOTPAdminSignInView,
)


urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('confirm_email_otp/', ConfirmEmailOTPView.as_view(), name='confirm_email_otp'),
    path('profile/<int:pk>/', ProfileRetrieveUpdateView.as_view(), name='profile'),
    path('verify-admin-otp/', ConfirmOTPAdminSignInView.as_view(), name='verify_admin_otp'),
]
