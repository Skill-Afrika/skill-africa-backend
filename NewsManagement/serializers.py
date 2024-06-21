from rest_framework import serializers
from .models import NewsFeed


class PostSerializer(serializers.ModelSerializer):
     class Meta:
          model = NewsFeed
          fields ='__all__'                               
                                                                                                               