from django.urls import include, path
from .views import GoogleStartSignInView, GoogleEndSignInView


urlpatterns = [
    path(
        "google/start/signin/<str:role>/",
        GoogleStartSignInView.as_view(),
        name="google_signin",
    ),
    path(
        "google/end/signin",
        GoogleEndSignInView.as_view(),
        name="google_signin_callback",
    ),
]

# urlpatterns = [
#     path(
#         "google/end/login/",
#         GoogleEndLoginView.as_view(),
#         name="oauth_end_login",
#     ),
#     path(
#         "google_sso/", include("django_google_sso.urls", namespace="django_google_sso")
#     ),
# ]
