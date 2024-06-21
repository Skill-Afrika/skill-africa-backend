from rest_framework import generics
from .models import Post        
from .serializers import PostSerializer   
from django.views.generic import ListView                      

class PostListCreate(generics.ListCreateAPIView):
    queryset = Post.objects.all() 
    serializer_class = PostSerializer


class PostDetails(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

class postlist(ListView):
    model=Post