import uuid
from datetime import timedelta
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.conf import settings

# ---------------- Base Problem ----------------
class BaseProblem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    statement = models.TextField()
    input_format = models.TextField(blank=True, null=True)
    output_format = models.TextField(blank=True, null=True)
    constraints = models.JSONField(blank=True, default=list)
    examples = models.JSONField(blank=True, default=list)  # [{'input': str, 'output': str, 'explanation': str}]
    test_cases = models.JSONField(blank=True, default=list)  # [{'input': str, 'output': str}]
    difficulty = models.CharField(max_length=10, choices=[('Easy', 'Easy'), ('Medium', 'Medium'), ('Hard', 'Hard')])
    tags = models.JSONField(blank=True, default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    attempts = models.IntegerField(default=0)
    solves = models.IntegerField(default=0)
    hardness_score = models.IntegerField(default=0, blank=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.title

# ---------------- Problems ----------------
class AdminProblem(BaseProblem):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

class CommunityProblem(BaseProblem):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

class AIProblem(BaseProblem):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # Add other fields as needed

# ---------------- Submission ----------------
class Submission(models.Model):
    STATUS_CHOICES = [
        ('Accepted', 'Accepted'),
        ('Wrong Answer', 'Wrong Answer'),
        ('Runtime Error', 'Runtime Error'),
        ('Time Limit Exceeded', 'Time Limit Exceeded'),
        ('Error', 'Error'),
        ('Pending', 'Pending'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)  # Fix: nullable for existing rows
    object_id = models.UUIDField(null=True, blank=True)  # Fix: nullable for existing rows
    problem = GenericForeignKey('content_type', 'object_id')
    code = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    runtime_ms = models.IntegerField(null=True, blank=True)
    memory_kb = models.IntegerField(null=True, blank=True)
    submitted_at = models.DateTimeField(default=timezone.now)  # default to avoid migration prompt

# ---------------- User Progress ----------------
class UserProgress(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)
    points = models.IntegerField(default=0)
    solved_count = models.IntegerField(default=0)
    current_streak = models.IntegerField(default=0)
    last_solve_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Progress"
