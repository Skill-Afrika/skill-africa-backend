from rest_framework import generics
from .models import Post        
from .serializers import PostSerializer                         

class PostListCreate(generics.ListCreateAPIView):
    queryset = Post.objects.all() 
    serializer_class = PostSerializer


class PostDetails(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
