from rest_framework import serializers
from .models import NewsFeed


class NewsFeedSerializer(serializers.ModelSerializer):
     """
    Serializer for News Feed
    """
     class Meta:
          model = NewsFeed
          fields ='__all__'
          read_only_fields = ['createdAt','id']
                               
                                                                                                               