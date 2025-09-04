# api/models/__init__.py
from .User import User, UserManager , SessionCode
from .resourcemodels import Document
from .UserProfileModel import UserProfiles

# This makes the models available as api.models.User
__all__ = ['User', 'UserManager', 'SessionCode', 'Document', 'UserProfiles']