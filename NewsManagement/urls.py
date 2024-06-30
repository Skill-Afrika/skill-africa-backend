from django.urls import path
from .views import NewsFeedCreateView,NewsFeedListView,NewsFeedDetails

urlpatterns = [
    path('newsfeed/',NewsFeedListView.as_view(),name='NewsFeed_list'),
    path('newsfeed/create/',NewsFeedCreateView.as_view(),name='NewsFeed_create'),
    path('newsfeed/<str:pk>/', NewsFeedDetails.as_view(),name='NewsFeed_details'),
]                                                              