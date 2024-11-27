from django.urls import path
from .views import (
    AddNicheView,
    AddSkillsView,
    DeleteNicheView,
    DeleteSkillView,
    FreelanceRegistrationView,
    FreelancerProfileList,
    FreelancerProfileDetail,
    FreelancerLinkListCreateView,
    FreelancerLinkDetailView,
    NicheCreateView,
    NicheListView,
    SkillListCreateView,
)

urlpatterns = [
    path(
        "register/", FreelanceRegistrationView.as_view(), name="freelance_registeration"
    ),
    path("profiles", FreelancerProfileList.as_view(), name="freelancer_profiles_list"),
    path(
        "profiles/<str:uuid>",
        FreelancerProfileDetail.as_view(),
        name="freelancer_profile_details",
    ),
    path(
        "profiles/<str:uuid>/links",
        FreelancerLinkListCreateView.as_view(),
        name="profile-link-list-create",
    ),
    path(
        "profiles/<str:uuid>/links/<int:linkId>",
        FreelancerLinkDetailView.as_view(),
        name="profile-link-detail",
    ),
    path(
        "profiles/<str:uuid>/skills",
        AddSkillsView.as_view(),
        name="add-freelancer-skills",
    ),
    path(
        "profiles/<str:uuid>/skills/delete",
        DeleteSkillView.as_view(),
        name="delete-freelancer-niches",
    ),
    path(
        "profiles/<str:uuid>/niches",
        AddNicheView.as_view(),
        name="add-freelancer-niches",
    ),
    path(
        "profiles/<str:uuid>/niches/delete",
        DeleteNicheView.as_view(),
        name="delete-freelancer-niches",
    ),
    path("niches", NicheListView.as_view(), name="niche-list"),
    path("niche", NicheCreateView.as_view(), name="niche-create"),
    path("skills", SkillListCreateView.as_view(), name="skill-list-create"),
]
