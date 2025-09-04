# from django.db import models
# from django.contrib import admin
# from .model import User

# class YourModel(models.Model):
#     name = models.CharField(max_length=100)
#     email = models.EmailField(unique=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     is_active = models.BooleanField(default=True)

#     def __str__(self):
#         return f"{self.name} ({self.email})"

# class RelatedModel(models.Model):
#     your_model = models.ForeignKey(YourModel, on_delete=models.CASCADE, related_name='related_items')
#     title = models.CharField(max_length=200)
#     description = models.TextField(blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.title

#     class Meta:
#         verbose_name = "Related Item"
#         verbose_name_plural = "Related Items"

# @admin.register(YourModel)
# class YourModelAdmin(admin.ModelAdmin):
#     list_display = ('name', 'email', 'created_at', 'is_active')

# @admin.register(RelatedModel)
# class RelatedModelAdmin(admin.ModelAdmin):
#     list_display = ('title', 'your_model', 'created_at')


# admin.site.register(User)

from django.contrib import admin
from api.model import User, SessionCode

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass

@admin.register(SessionCode)
class SessionCodeAdmin(admin.ModelAdmin):
    pass