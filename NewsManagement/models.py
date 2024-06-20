from django.db import models
import uuid


class Post(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4, editable=False)
    title= models.CharField(verbose_name='titles',max_length=200)
    content=models.TextField()
    createdAt=models.DateField(auto_now_add=True)