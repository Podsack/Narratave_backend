from django.contrib import admin

from .models import User


class UserAdmin(admin.ModelAdmin):
    exclude = ('is_staff', 'is_superuser', 'password', 'last_login', 'user_permissions', 'groups')
    list_display = ('id', 'email', 'role', 'first_name', 'last_name', 'profile_picture', 'last_login', 'dob')


admin.site.register(User, UserAdmin)
