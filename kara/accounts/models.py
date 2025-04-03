from django.contrib.auth.models import AbstractUser
from django.db import models

from .fields import DefaultOneToOneField


class User(AbstractUser):
    first_name = None
    last_name = None


class UserProfile(models.Model):
    user = DefaultOneToOneField(
        User, create=True, on_delete=models.CASCADE, related_name="profile"
    )
    bio = models.TextField(blank=True, null=True)
    bio_image = models.ImageField(blank=True, null=True)
    email_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username
