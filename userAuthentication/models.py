"""
Holds models of users
"""
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class CustomUser(AbstractUser):
    """
    Holds custom user data
    """
    name = models.CharField(max_length=150, blank=False, default="User")
    groups = models.ManyToManyField(
        Group,
        related_name='customuser_set',  # Ensure this is unique
        blank=True,
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_permissions_set',  # Ensure this is unique
        blank=True,
        verbose_name='user permissions',
    )
