from django.urls import include, path
from .views import GoogleStartLoginView

urlpatterns = [
    path("google/login/", GoogleStartLoginView.as_view(), name="oauth_start_login"),
    path(
        "google_sso/", include("django_google_sso.urls", namespace="django_google_sso")
    ),
]
