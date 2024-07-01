from django.contrib import admin
from .models import SponsorProfile

class SponsorAdmin(admin.ModelAdmin):
    # list_display = ('id', 'user', 'email')
    # search_fields = ('user__username', 'user__email')
    pass

admin.site.register(SponsorProfile, SponsorAdmin)