from rest_framework import serializers
from ..model.dsa_model import Problem, Submission, Progress


class ProblemListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for problem list view"""

    class Meta:
        model = Problem
        fields = ["id", "title", "difficulty", "tags", "points"]


class ProblemDetailSerializer(serializers.ModelSerializer):
    """Detailed problem serializer (hides hidden_tests)"""

    class Meta:
        model = Problem
        exclude = ["hidden_tests"]  


class SubmissionSerializer(serializers.ModelSerializer):
    problem_title = serializers.ReadOnlyField(source="problem.title")  

    class Meta:
        model = Submission
        fields = ["id", "problem", "problem_title", "code", "result", "created_at"]
        read_only_fields = ["result", "created_at"]  

class ProgressSerializer(serializers.ModelSerializer):
    """Serialize user progress (points only)"""

    class Meta:
        model = Progress
        fields = ["points"]
