from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission
from django.utils import timezone

class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        if not username:
            raise ValueError('The Username field must be set')
        
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        return self.create_user(username, email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255, blank=True)
    
    # JWT & Firebase Integration Fields
    firebase_uid = models.CharField(
        max_length=128, 
        unique=True, 
        null=True, 
        blank=True,
        db_index=True
    )
    provider = models.CharField(
        max_length=50, 
        default='email',
        choices=[
            ('email', 'Email'),
            ('google', 'Google'),
            ('github', 'GitHub'),
        ]
    )
    avatar_url = models.URLField(blank=True)
    
    # Timestamps
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Status fields
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    
    # Django auth relationships
    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        related_name='api_user_set',
        related_query_name='user',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        related_name='api_user_set',
        related_query_name='user',
    )
    
    objects = UserManager()
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
    
    class Meta:
        db_table = 'auth_user'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['firebase_uid']),
            models.Index(fields=['provider']),
            models.Index(fields=['date_joined']),
        ]
    
    def __str__(self):
        return self.username
    
    def get_full_name(self):
        return self.full_name
    
    def get_short_name(self):
        if self.full_name:
            return self.full_name.split()[0] if ' ' in self.full_name else self.full_name
        return self.username
    
    @property
    def display_name(self):
        """Return the best available display name"""
        return self.full_name or self.username
    
    def update_from_firebase(self, firebase_user_data):
        """Update user data from Firebase authentication"""
        if firebase_user_data.get('email') and self.email != firebase_user_data['email']:
            self.email = firebase_user_data['email']
        if firebase_user_data.get('full_name') and not self.full_name:
            self.full_name = firebase_user_data['full_name']
        if firebase_user_data.get('avatar_url') and not self.avatar_url:
            self.avatar_url = firebase_user_data['avatar_url']
        if firebase_user_data.get('provider'):
            self.provider = firebase_user_data['provider']
        self.save()

class JWTToken(models.Model):
    """
    Optional: Store JWT tokens for blacklisting or tracking
    Not required for basic JWT functionality
    """
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='jwt_tokens'
    )
    jti = models.CharField(
        max_length=64, 
        unique=True, 
        db_index=True,
        help_text="JWT Token ID"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(db_index=True)
    is_blacklisted = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'auth_jwt_token'
        indexes = [
            models.Index(fields=['jti']),
            models.Index(fields=['expires_at']),
            models.Index(fields=['is_blacklisted']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.jti}"
    
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    @property
    def is_valid(self):
        return not self.is_expired and not self.is_blacklisted

class UserProfiles(models.Model):
    """
    Extended user profile for additional information
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    bio = models.TextField(blank=True, max_length=500 , default="")
    website = models.URLField(blank=True)
    location = models.CharField(max_length=100, blank=True , default="")
    
    # Social links
    github_username = models.CharField(max_length=39, blank=True)
    twitter_username = models.CharField(max_length=15, blank=True)
    linkedin_url = models.URLField(blank=True)
    
    # Preferences
    email_notifications = models.BooleanField(default=True)
    theme_preference = models.CharField(
        max_length=20,
        choices=[
            ('light', 'Light'),
            ('dark', 'Dark'),
            ('auto', 'Auto'),
        ],
        default='auto'
    )

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'auth_user_profile'
    
    def __str__(self):
        return f"Profile of {self.user.username}"

# Signals to create profile automatically
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Automatically create user profile when a new user is created
    """
    if created:
        UserProfiles.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Automatically save user profile when user is saved
    """
    if hasattr(instance, 'profile'):
        instance.profile.save()