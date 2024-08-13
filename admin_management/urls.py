from django.urls import path
from .views import AdminProfileDetail, AdminRegistrationView, AdminProfileList

urlpatterns = [
    path("register/", AdminRegistrationView.as_view(), name="admin_registeration"),
    path("profiles", AdminProfileList.as_view(), name="admin_profiles_list"),
    path(
        "profiles/<str:uuid>",
        AdminProfileDetail.as_view(),
        name="admin_profile_details",
    ),
]
