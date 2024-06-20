from django.contrib import admin
from .models import AdminProfile


class AdminAdmin(admin.ModelAdmin):
    # list_display = ('id', 'user', 'email')
    # search_fields = ('user__username', 'user__email')
    pass

admin.site.register(AdminProfile, AdminAdmin)