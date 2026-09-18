from django.contrib import admin
from userauths.models import User, Profile


class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'full_name', 'role', 'is_staff', 'is_active']
    list_filter = ['role', 'is_staff', 'is_active']
    search_fields = ['email', 'full_name', 'username']


class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'full_name', 'date']


admin.site.register(User, UserAdmin)
admin.site.register(Profile, ProfileAdmin)
