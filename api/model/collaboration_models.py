from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

# Use the canonical User model defined in api.model.User
from .User import User

class Project(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    tech_stack = models.JSONField(default=list)
    skills_needed = models.JSONField(default=list)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_projects')
    members = models.ManyToManyField(User, related_name='projects')
    is_public = models.BooleanField(default=True)
    github_repo = models.URLField(blank=True, null=True)
    demo_url = models.URLField(blank=True, null=True)
    club = models.ForeignKey('Club', on_delete=models.SET_NULL, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'projects'

class MentorSession(models.Model):
    mentor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mentor_sessions')
    mentee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mentee_sessions')
    date = models.DateTimeField()
    duration = models.IntegerField(help_text="Duration in minutes")
    notes = models.TextField()
    rating = models.FloatField(blank=True, null=True, validators=[MinValueValidator(0), MaxValueValidator(5)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'mentor_sessions'

class Community(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    members = models.ManyToManyField(User, related_name='communities')
    is_public = models.BooleanField(default=True)
    topics = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'communities'

class Club(models.Model):
    CATEGORY_CHOICES = [
        ('coding', 'Coding'),
        ('design', 'Design'),
        ('research', 'Research'),
        ('entrepreneurship', 'Entrepreneurship'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='coding')
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name='administered_clubs')
    members = models.ManyToManyField(User, through='ClubMember', related_name='clubs')
    is_public = models.BooleanField(default=True)
    tags = models.JSONField(default=list)
    college = models.CharField(max_length=200)
    mission_statement = models.TextField()
    core_focus = models.JSONField(default=list)
    faculty_advisor = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='advised_clubs')
    social_links = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'clubs'

class ClubMember(models.Model):
    ROLE_CHOICES = [
        ('president', 'President'),
        ('vice_president', 'Vice President'),
        ('technical_head', 'Technical Head'),
        ('marketing_head', 'Marketing Head'),
        ('treasurer', 'Treasurer'),
        ('event_coordinator', 'Event Coordinator'),
        ('member', 'Member'),
    ]
    
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'club_members'
        unique_together = ['club', 'user']

class ClubEvent(models.Model):
    EVENT_TYPE_CHOICES = [
        ('workshop', 'Workshop'),
        ('talk', 'Talk'),
        ('coding_session', 'Coding Session'),
        ('project', 'Project'),
        ('guest_talk', 'Guest Talk'),
        ('hackathon', 'Hackathon'),
        ('social', 'Social'),
    ]
    
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='events')
    title = models.CharField(max_length=200)
    description = models.TextField()
    type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES, default='workshop')
    date = models.DateTimeField()
    location = models.CharField(max_length=200)
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organized_events')
    attendees = models.ManyToManyField(User, related_name='attended_events', blank=True)
    registered_attendees = models.ManyToManyField(User, related_name='registered_events', blank=True)
    max_attendees = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'club_events'

class ClubPost(models.Model):
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='club_posts')
    tags = models.JSONField(default=list)
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'club_posts'

class ClubResources(models.Model):
    RESOURCE_TYPE_CHOICES = [
        ('document', 'Document'),
        ('template', 'Template'),
        ('guide', 'Guide'),
        ('recording', 'Recording'),
    ]
    
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='resources')
    name = models.CharField(max_length=200)
    type = models.CharField(max_length=20, choices=RESOURCE_TYPE_CHOICES, default='document')
    url = models.URLField()
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_resources')
    downloads = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'club_resources'

class ProjectGroup(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='groups')
    members = models.ManyToManyField(User, related_name='project_groups')
    skills = models.JSONField(default=list)
    looking_for = models.JSONField(default=list)
    max_members = models.IntegerField(default=4)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'project_groups'