from django.urls import path
from .views import FreelanceRegistrationView, SponsorRegistrationView, AdminRegistrationView, LoginView

urlpatterns = [
    path('users/register/', FreelanceRegistrationView.as_view(), name='freelance_registeration'),
    path('users/login/', LoginView.as_view(), name='login_view'),
    path('sponsors/register/', SponsorRegistrationView.as_view(), name='freelance_registeration'),
    path('admins/register/', AdminRegistrationView.as_view(), name='freelance_registeration'),
]