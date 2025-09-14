from django.db import models
from ..model.User import User  # ✅ adjust import path to your project structure


class Problem(models.Model):
    DIFFICULTY_CHOICES = [
        ("Easy", "Easy"),
        ("Medium", "Medium"),
        ("Hard", "Hard"),
    ]

    title = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True, null=True)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES)
    tags = models.JSONField(default=list, blank=True)  # store as ["array", "of", "tags"]
    examples = models.JSONField(default=list, blank=True)  # [{"input": "1", "output": "2"}]
    hidden_tests = models.JSONField(default=list, blank=True)  # backend only
    points = models.PositiveIntegerField(default=0)  # ✅ non-negative
    starter_code = models.TextField(blank=True, null=True)
    solution = models.TextField(blank=True, null=True)  # canonical solution

    created_at = models.DateTimeField(auto_now_add=True)  # ✅ track problem creation
    updated_at = models.DateTimeField(auto_now=True)      # ✅ track updates

    class Meta:
        ordering = ["difficulty", "-points", "title"]

    def __str__(self):
        return f"{self.title} ({self.difficulty})"


class Submission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name="submissions")
    code = models.TextField()
    result = models.JSONField(blank=True, null=True)  # stores run results
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        username = self.user.username if self.user else "Anonymous"
        return f"Submission for {self.problem.title} by {username}"


class Progress(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name="progress")
    points = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        username = self.user.username if self.user else "Anonymous"
        return f"Progress({username}): {self.points}"
