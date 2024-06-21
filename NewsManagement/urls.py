from django.urls import path
from .views import PostListCreate,PostDetails,postlist

urlpatterns = [
    path('posts/', PostListCreate.as_view(), name = 'post_list_create'),
    path('posts/<uuidr:id >/', PostDetails.as_view(), name='post_details'),
    path('posts/list',postlist.as_view(), name='post_list' ),
]                                                             