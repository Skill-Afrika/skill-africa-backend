from django.urls import include, path

urlpatterns = [
    path(
        "google_sso/", include("django_google_sso.urls", namespace="django_google_sso")
    ),
]
