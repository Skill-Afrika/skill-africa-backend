from django.contrib import admin
from .models import FreelancerProfile, SponsorProfile, AdminProfile

class FreelancerAdmin(admin.ModelAdmin):
    # list_display = ('id', 'user', 'email')
    # search_fields = ('user__username', 'user__email')
    pass

class SponsorAdmin(admin.ModelAdmin):
    # list_display = ('id', 'user', 'email')
    # search_fields = ('user__username', 'user__email')
    pass

class AdminAdmin(admin.ModelAdmin):
    # list_display = ('id', 'user', 'email')
    # search_fields = ('user__username', 'user__email')
    pass

admin.site.register(FreelancerProfile, FreelancerAdmin)
admin.site.register(SponsorProfile, SponsorAdmin)
admin.site.register(AdminProfile, AdminAdmin)