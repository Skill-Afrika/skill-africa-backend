from django.urls import path
from .views import NewsFeedCreateView,NewsFeedListView,NewsFeedDetails

urlpatterns = [
    path('',NewsFeedListView.as_view(),name='NewsFeed_list'),
    path('create/',NewsFeedCreateView.as_view(),name='NewsFeed_create'),
    path('<str:pk>/', NewsFeedDetails.as_view(),name='NewsFeed_details'),
]                                                              