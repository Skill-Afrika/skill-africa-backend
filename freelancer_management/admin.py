from django.contrib import admin
from .models import FreelancerProfile

class FreelancerAdmin(admin.ModelAdmin):
    # list_display = ('id', 'user', 'email')
    # search_fields = ('user__username', 'user__email')
    pass

admin.site.register(FreelancerProfile, FreelancerAdmin)