from django.contrib import admin

from users.models import User


@admin.register(User)
class UserAdminModel(admin.ModelAdmin):
    list_display = ("id", "email")
