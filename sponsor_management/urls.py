from django.urls import path
from .views import SponsorRegistrationView

urlpatterns = [
    path('register/', SponsorRegistrationView.as_view(), name='freelance_registeration'),
]