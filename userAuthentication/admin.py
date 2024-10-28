# admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    # Specify the fields to display in the admin list view
    list_display = ('username', 'email', 'name', 'is_staff')

    # Specify the fields to edit in the detail view
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('name',)}),  # Add the name field here
    )


admin.site.register(CustomUser, CustomUserAdmin)
