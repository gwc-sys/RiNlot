# api/models/__init__.py
from .User import User, UserManager , SessionCode
from .resourcemodels import Document
from .UserProfileModel import UserProfiles
from .dsa_problem_model import AdminProblem, CommunityProblem, AIProblem, Submission, UserProgress , ContentType

# This makes the models available as api.models.User
__all__ = ['User', 'UserManager', 'SessionCode', 'Document', 'UserProfiles', 'AdminProblem', 'CommunityProblem', 'AIProblem', 'Submission', 'UserProgress', 'ContentType']