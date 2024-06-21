from rest_framework import generics
from .models import NewsFeed        
from .serializers import PostSerializer   
from django.views.generic import ListView                      

#things to do
#create the postcreate class differently api/newsfeed/create (admin only)
#create the postlist class differently api/newsfeed/
#also write the schema for documentation

class PostListCreate(generics.ListCreateAPIView):
    queryset = NewsFeed.objects.all() 
    serializer_class = PostSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

#this stands for the api/newsfeed/<id>
# remember only admin can do this 
class PostDetails(generics.RetrieveUpdateDestroyAPIView):
    queryset = NewsFeed.objects.all()
    serializer_class = PostSerializer

#class postlist(ListView):
  