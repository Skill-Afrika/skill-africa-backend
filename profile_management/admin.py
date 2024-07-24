from django.contrib import admin
from .models import User, PasswordOTP


class UserAdmin(admin.ModelAdmin):
    # list_display = ('id', 'user', 'email')
    # search_fields = ('user__username', 'user__email')
    pass


admin.site.register(User, UserAdmin)


class OTPAdmin(admin.ModelAdmin):
    pass


admin.site.register(PasswordOTP, OTPAdmin)
