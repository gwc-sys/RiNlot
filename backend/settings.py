import os
from pathlib import Path
import mysql.connector
import mysql.connector
from decouple import config



# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-fhipcgf5kce18*wz5e7$cu!s59&(j%1cv7c!fcaxa4_6^13!8%'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'api',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'cloudinary',
    'cloudinary_storage',
    'rest_framework', 
    'corsheaders'
]

AUTH_USER_MODEL = 'api.User'  # Update this line to point to the correct app and model


MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
]

ROOT_URLCONF = 'backend.urls'

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

WSGI_APPLICATION = 'backend.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases


# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'myengiportaldb',
#         'USER': 'root',
#         'PASSWORD': 'N!uos0G375',
#         'HOST': 'localhost',
#         'PORT': '3306',
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT', cast=int),
        'OPTIONS': {
            'ssl': {
                'ssl_ca': "django_backend/certs/ca.pem",
                'ssl-mode': 'REQUIRED'
            },
            'connect_timeout': 30, 
        }
    }
    
}




# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Cloudinary settings
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': 'dthdececa',
    'API_KEY': '354378824539823',
    'API_SECRET': 'EWuAT6UFwupVh1E4TtJtILeUszY',
    'SECURE': True
}


DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
# For production (specific domain)
ALLOWED_HOSTS = ['engiportal.onrender.com']


# Recommended approach for Render.com deployments
ALLOWED_HOSTS = [
    'engiportal.onrender.com',
    '.onrender.com',
    'localhost',
    '127.0.0.1',
    '0.0.0.0',
    'stackhack.live',
]
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:5174",
    "https://engisolution.onrender.com",
    "http://localhost:5173",   
    "http://127.0.0.1",        
    "http://localhost",        
    "https://engiportal.onrender.com",
    "https://stackhack.live"
]
CSRF_TRUSTED_ORIGINS = [
    "https://engisolution.onrender.com",
    "http://localhost:5173",
    "http://0.0.0.0:5173",
    "http://127.0.0.1:5173",
    "http://0.0.0.0:8000",
    "https://stackhack.live"
]

import logging

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

# File upload size limits
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}



