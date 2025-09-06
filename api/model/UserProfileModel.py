from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

def validate_image_size(value):
    """Validate that image size doesn't exceed 2MB"""
    limit = 2 * 1024 * 1024
    if value.size > limit:
        raise ValidationError('Image too large. Size should not exceed 2MB.')

def user_profile_picture_path(instance, filename):
    """Generate user-specific upload path"""
    return f"profile_pictures/user_{instance.user.id}/{filename}"

class UserProfiles(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="profile"
    )
    phone = models.CharField(max_length=20, blank=True, null=True)
    profile_picture = models.ImageField(
        upload_to=user_profile_picture_path,
        validators=[validate_image_size],
        blank=True, 
        null=True
    )
    bio = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)

    # Flexible JSON fields
    social_links = models.JSONField(default=dict, blank=True)
    skills = models.JSONField(default=list, blank=True)
    interests = models.JSONField(default=list, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}'s Profile"

    @property
    def initials(self):
        """Return initials from full name or username"""
        full_name = self.user.get_full_name()
        if full_name:
            parts = full_name.split()
            if len(parts) >= 2:
                return f"{parts[0][0]}{parts[-1][0]}".upper()
            return parts[0][0].upper()
        return self.user.username[0].upper() if self.user.username else "U"

    @property
    def display_name(self):
        """Return display name: full name or username"""
        return self.user.get_full_name() or self.user.username

    def get_social_link(self, platform):
        """Helper to get specific social link"""
        return self.social_links.get(platform, "")