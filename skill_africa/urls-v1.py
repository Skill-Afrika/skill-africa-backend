from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path("", include("api.urls")),
    path("users/", include("profile_management.urls")),
    path("admins/", include("admin_management.urls")),
    path("events/", include("event_management.urls")),
    path("freelancer/", include("freelancer_management.urls")),
    path("sponsors/", include("sponsor_management.urls")),
    path("newsfeed/", include("news_management.urls")),
    # path("auth/", include("dj_rest_auth.urls")),
    # path("auth/registration/", include("dj_rest_auth.registration.urls")),
    path("sso/", include("sso_authentication.urls")),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("docs/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]

