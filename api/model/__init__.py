# api/models/__init__.py
from .User import User, UserManager , SessionCode
from .resourcemodels import Document

# This makes the models available as api.models.User
__all__ = ['User', 'UserManager', 'SessionCode', 'Document']