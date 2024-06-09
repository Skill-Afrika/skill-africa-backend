from django.urls import path
from .models import CustomUser

urlpatterns  = [
    path('',CustomUser, name= 'customuser')
]