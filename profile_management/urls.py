from django.urls import path
from .views import (
    LoginView,
    LogoutView,
    ConfirmEmail,
    PasswordOTPView,
    VerifyOTPView,
)
from dj_rest_auth.views import (
    PasswordChangeView,
)
from dj_rest_auth.registration.views import VerifyEmailView, ResendEmailVerificationView

urlpatterns = [
    path("login/", LoginView.as_view(), name="login_view"),
    path("logout/", LogoutView.as_view(), name="logout_view"),
    path("password/change/", PasswordChangeView.as_view(), name="password_change"),
    path(
        "password/otp/",
        PasswordOTPView.as_view(),
        name="password_otp",
    ),
    path(
        "password/otp/<str:uuid>",
        VerifyOTPView.as_view(),
        name="password_otp_confirm",
    ),
    path(
        r"confirm/email/<str:key>",
        ConfirmEmail.as_view(),
        name="account_confirm_email",
    ),
    path("resend/email/", ResendEmailVerificationView.as_view(), name="resend_email"),
    path("verify/email/", VerifyEmailView.as_view(), name="verify_email"),
]
