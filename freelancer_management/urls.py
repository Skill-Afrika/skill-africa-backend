from django.urls import path
from .views import FreelanceRegistrationView

urlpatterns = [
    path(
        "register/", FreelanceRegistrationView.as_view(), name="freelance_registeration"
    ),
]
