from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


# admin.site.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('id','first_name','last_name','email','phone_number','username','password',)
admin.site.register(CustomUser, CustomUserAdmin)
