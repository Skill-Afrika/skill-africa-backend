from django.urls import path
from .views import LoginView

urlpatterns = [
    path('users/login/', LoginView.as_view(), name='login_view'),
]