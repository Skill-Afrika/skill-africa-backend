from django.urls import path
from .views import PostListCreate,PostDetails

urlpatterns = [
    path('posts/', PostListCreate.as_view(), name = 'post_list_create'),
    path('posts/<id>/', PostDetails.as_view(), name='post_details'), 
 ]                                                             