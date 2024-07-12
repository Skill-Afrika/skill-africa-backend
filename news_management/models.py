from django.db import models
import uuid
from django.contrib.auth.models import User
from profile_management.models import ProfileBase


class NewsFeed(ProfileBase):
    
    title = models.CharField(verbose_name='titles', max_length=200)
    content = models.TextField()
    createdAt = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.title
