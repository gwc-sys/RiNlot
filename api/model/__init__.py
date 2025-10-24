# api/models/__init__.py
from .User import User, UserManager , UserProfiles , JWTToken 
from .resourcemodels import Document
# from .UserProfileModel import UserProfiless
from .dsa_problem_model import AdminProblem, CommunityProblem, AIProblem, Submission, UserProgress , ContentType
from .collaboration_models import Project, MentorSession, Community, Club, ClubMember, ClubEvent, ClubPost, ClubResources, ProjectGroup

# This makes the models available as api.models.User
__all__ = ['User', 'UserManager', 'Document', 'UserProfiles', 'AdminProblem', 'CommunityProblem', 'AIProblem', 'Submission', 'UserProgress', 'ContentType', 'Project', 'MentorSession', 'Community',
            'Club', 'ClubMember', 'ClubEvent', 'ClubPost', 'ClubResources', 'ProjectGroup', 'JWTToken']