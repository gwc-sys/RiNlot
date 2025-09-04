from .model.User import SessionCode
from .model.User import User
from django.db import models

# class UserProfile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     bio = models.TextField(blank=True)
#     location = models.CharField(max_length=100, blank=True)
#     birth_date = models.DateField(null=True, blank=True)
#     avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)