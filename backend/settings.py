"""
Django settings for backend project.
"""

import os
import logging
from pathlib import Path
from decouple import config
from pytz import timezone

# Build paths inside the project like this: BASE_DIR / 'subdir'
BASE_DIR = Path(__file__).resolve().parent.parent

# Security Settings
SECRET_KEY = config('SECRET_KEY', default='django-insecure-fhipcgf5kce18*wz5e7$cu!s59&(j%1cv7c!fcaxa4_6^13!8%')
DEBUG = config('DEBUG', default=True, cast=bool)

# Application definition
INSTALLED_APPS = [
    # Django core apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party apps
    'cloudinary',
    'cloudinary_storage',
    'rest_framework', 
    'corsheaders',
    
    # Local apps
    'api',
]

MIDDLEWARE = [
    # Security middleware
    'django.middleware.security.SecurityMiddleware',
    
    # Session middleware
    'django.contrib.sessions.middleware.SessionMiddleware',
    
    # CORS middleware (placed before CommonMiddleware)
    'corsheaders.middleware.CorsMiddleware',
    
    # Common middleware
    'django.middleware.common.CommonMiddleware',
    
    # CSRF protection
    'django.middleware.csrf.CsrfViewMiddleware',
    
    # Authentication middleware
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    
    # Message middleware
    'django.contrib.messages.middleware.MessageMiddleware',
    
    # Clickjacking protection
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'backend.urls'
WSGI_APPLICATION = 'backend.wsgi.application'

# Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT', default=3306, cast=int),
        'OPTIONS': {
            'ssl': {
                'ssl_ca': BASE_DIR / "certs/ca.pem",
                'ssl-mode': 'REQUIRED'
            },
            'connect_timeout': 30, 
        }
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# Media files
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom user model
AUTH_USER_MODEL = 'api.User'

# REST Framework configuration
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
}

# File upload settings
DATA_UPLOAD_MAX_MEMORY_SIZE = 52428800   # 50MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 52428800   # 50MB


# Cloudinary settings
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': config('CLOUDINARY_CLOUD_NAME', default='dj3jyvgir'),
    'API_KEY': config('CLOUDINARY_API_KEY', default='316446613211394'),
    'API_SECRET': config('CLOUDINARY_API_SECRET', default='-njAUsjKFpgKVBDBRp6xxX5r1zU'),
    'SECURE': True
}
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

# Host/domain names that this site can serve
ALLOWED_HOSTS = [
    'engiportal.onrender.com',
    '.onrender.com',
    'localhost',
    '127.0.0.1',
    '0.0.0.0',
    'stackhack.live',
]

# CORS settings
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:5174",
    "https://engisolution.onrender.com",
    "http://127.0.0.1",        
    "http://localhost",        
    "https://engiportal.onrender.com",
    "https://stackhack.live",
]

CSRF_TRUSTED_ORIGINS = [
    "https://engisolution.onrender.com",
    "http://localhost:5173",
    "http://0.0.0.0:5173",
    "http://127.0.0.1:5173",
    "http://0.0.0.0:8000",
    "https://stackhack.live"
]

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization', 
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'x-session-code',  # Custom header
]

# Logging configuration
IGNORABLE_404_URLS = [
    r'^\.well-known/appspecific/com\.chrome\.devtools\.json$',
]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        }
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',  # Only log errors, not 404s
            'propagate': True,
        },
    }
}

# Utility function for time conversion
def get_local_time(utc_time):
    """Convert UTC time to local time."""
    return timezone.localtime(utc_time)