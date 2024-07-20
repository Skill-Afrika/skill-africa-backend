from django.contrib import admin
from .models import NewsFeed

class NewsFeedAdmin(admin.ModelAdmin):
    pass

admin.site.register(NewsFeed, NewsFeedAdmin)