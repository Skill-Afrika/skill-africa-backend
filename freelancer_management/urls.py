from django.urls import path
from .views import (
    FreelanceRegistrationView,
    FreelancerProfileList,
    FreelancerProfileDetail,
)

urlpatterns = [
    path(
        "register/", FreelanceRegistrationView.as_view(), name="freelance_registeration"
    ),
    path("profiles/", FreelancerProfileList.as_view(), name="freelancer_profiles_list"),
    path(
        "profiles/<str:uuid>",
        FreelancerProfileDetail.as_view(),
        name="freelancer_profile_details",
    ),
]
