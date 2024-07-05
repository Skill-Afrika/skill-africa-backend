from django.urls import path
from .views import (
    LoginView,
    LogoutView,
    ResendEmail,
    VerifyEmail,
    PasswordChange,
    PasswordReset,
    PasswordResetConfirm,
    ConfirmEmail,
)

urlpatterns = [
    path("login/", LoginView.as_view(), name="login_view"),
    path("logout/", LogoutView.as_view(), name="logout_view"),
    path("password/change", PasswordChange.as_view(), name="password_change"),
    path("password/reset/", PasswordReset.as_view(), name="password_reset"),
    path(
        "password/confirm/",
        PasswordResetConfirm.as_view(),
        name="password_confirm",
    ),
    path(
        r"confirm/email/(?P<key>[-:\w]+)/$",
        ConfirmEmail.as_view(),
        name="account_confirm_email",
    ),
    path("resend/email/", ResendEmail.as_view(), name="resend_email"),
    path("verify/email/", VerifyEmail.as_view(), name="verify_email"),
]
