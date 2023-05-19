from django.urls import path
from .views import register_user, verify_otp, login

urlpatterns = [
    path('register/', register_user, name='register'),
    path('verify-otp/', verify_otp, name='verify_otp'),
    path('login/', login, name='login'),
]

