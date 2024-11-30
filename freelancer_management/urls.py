from django.urls import path

from freelancer_management.views.language import (
    AddLanguageView,
    DeleteLanguageView,
    LanguageListCreateView,
)
from freelancer_management.views.links import (
    FreelancerLinkDetailView,
    FreelancerLinkListCreateView,
)
from freelancer_management.views.niche import (
    AddNicheView,
    DeleteNicheView,
    NicheCreateView,
    NicheListView,
)
from freelancer_management.views.profile import (
    FreelanceRegistrationView,
    FreelancerProfileDetail,
    FreelancerProfileList,
    ProfilePictureDeleteView,
    ProfilePictureUploadView,
)
from freelancer_management.views.projects import (
    CoverImageDeleteView,
    CoverImageUploadView,
    ProjectCreateView,
    ProjectDeleteView,
    ProjectListView,
)
from freelancer_management.views.skills import (
    AddSkillsView,
    DeleteSkillView,
    SkillListCreateView,
)
from freelancer_management.views.work_experience import (
    ResumeDeleteView,
    ResumeUploadView,
    WorkExperienceCreateView,
    WorkExperienceDeleteView,
    WorkExperienceListView,
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
        "profiles/picture/<str:uuid>/upload",
        ProfilePictureUploadView.as_view(),
        name="profile_picture_upload",
    ),
    path(
        "profiles/picture/<str:uuid>/delete",
        ProfilePictureDeleteView.as_view(),
        name="profile_picture_delete",
    ),
    # Links urls
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
    # Skills urls
    path(
        "profiles/<str:uuid>/skills",
        AddSkillsView.as_view(),
        name="add-freelancer-skills",
    ),
    path(
        "profiles/<str:uuid>/skills/delete",
        DeleteSkillView.as_view(),
        name="delete-freelancer-skills",
    ),
    path("skills", SkillListCreateView.as_view(), name="skill-list-create"),
    # Skills urls
    path(
        "profiles/<str:uuid>/languages",
        AddLanguageView.as_view(),
        name="add-freelancer-languages",
    ),
    path(
        "profiles/<str:uuid>/languages/delete",
        DeleteLanguageView.as_view(),
        name="delete-freelancer-languages",
    ),
    path("languages", LanguageListCreateView.as_view(), name="language-list-create"),
    # Niche urls
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
    # Project urls
    path(
        "profiles/<str:uuid>/projects",
        ProjectListView.as_view(),
        name="project-list",
    ),
    path(
        "profiles/<str:uuid>/project",
        ProjectCreateView.as_view(),
        name="project-create",
    ),
    path(
        "profiles/<str:uuid>/project/<int:id>",
        ProjectDeleteView.as_view(),
        name="project-delete",
    ),
    path(
        "profiles/<str:uuid>/project/coverimage/<int:id>/upload",
        CoverImageUploadView.as_view(),
        name="project_cover_image_upload",
    ),
    path(
        "profiles/<str:uuid>/project/coverimage/<int:id>/delete",
        CoverImageDeleteView.as_view(),
        name="project_cover_image_delete",
    ),
    # Work Experience Urls
    path(
        "profiles/<str:uuid>/work-experiences",
        WorkExperienceListView.as_view(),
        name="work-experience-list",
    ),
    path(
        "profiles/<str:uuid>/work-experience",
        WorkExperienceCreateView.as_view(),
        name="work-experience-create",
    ),
    path(
        "profiles/<str:uuid>/work-experience/<int:id>",
        WorkExperienceDeleteView.as_view(),
        name="work-experience-delete",
    ),
    path(
        "profiles/resume/<str:uuid>/upload",
        ResumeUploadView.as_view(),
        name="resume_upload",
    ),
    path(
        "profiles/resume/<str:uuid>/delete",
        ResumeDeleteView.as_view(),
        name="resume_delete",
    ),
]
