# skill_africa_backend/api/urls.py
from django.urls import path
from .views import under_construction

urlpatterns = [
    path('under-construction/', under_construction, name='under_construction'),
]
