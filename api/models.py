from django.db import models
from django.contrib.auth.models import AbstractUser
# django.contrib.auth.models.AbstractUser

class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=15, unique=True)
    is_verified = models.BooleanField(default=False)
