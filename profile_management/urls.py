from django.urls import path
from .views import FreelanceRegistrationView, SponsorRegistrationView, AdminRegistrationView

urlpatterns = [
    path('users/register/', FreelanceRegistrationView.as_view(), name='freelance_registeration'),
    path('sponsors/register/', SponsorRegistrationView.as_view(), name='freelance_registeration'),
    path('admins/register/', AdminRegistrationView.as_view(), name='freelance_registeration'),
]