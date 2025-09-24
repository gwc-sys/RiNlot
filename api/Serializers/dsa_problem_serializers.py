from rest_framework import serializers
from ..model import AdminProblem, CommunityProblem, AIProblem, UserProgress, Submission, ContentType

class BaseProblemSerializer(serializers.ModelSerializer):
    source = serializers.SerializerMethodField()
    success_rate = serializers.SerializerMethodField()
    user_solved = serializers.SerializerMethodField()

    def get_success_rate(self, obj):
        if obj.attempts == 0:
            return 0
        return round((obj.solves / obj.attempts) * 100, 1)

    def get_user_solved(self, obj):
        user = self.context['request'].user
        if not user.is_authenticated:
            return False
        ct = ContentType.objects.get_for_model(obj.__class__)
        return Submission.objects.filter(user=user, content_type=ct, object_id=obj.id, status='Accepted').exists()

    class Meta:
        fields = [
            'id', 'title', 'statement', 'input_format', 'output_format', 'constraints', 'examples',
            'difficulty', 'tags', 'created_at', 'author', 'source', 'attempts', 'solves',
            'hardness_score', 'user_solved', 'success_rate'
        ]
        read_only_fields = ['id', 'created_at', 'author', 'source', 'attempts', 'solves', 'hardness_score']

class AdminProblemSerializer(BaseProblemSerializer):
    def get_source(self, obj):
        return 'Admin'

    class Meta(BaseProblemSerializer.Meta):
        model = AdminProblem

class CommunityProblemSerializer(BaseProblemSerializer):
    def get_source(self, obj):
        return 'User'

    class Meta(BaseProblemSerializer.Meta):
        model = CommunityProblem

class AIProblemSerializer(BaseProblemSerializer):
    def get_source(self, obj):
        return 'AI'

    class Meta(BaseProblemSerializer.Meta):
        model = AIProblem
        read_only_fields = BaseProblemSerializer.Meta.read_only_fields + ['author']

class UserProgressSerializer(serializers.ModelSerializer):
    user_id = serializers.CharField(source='user.id')
    name = serializers.CharField(source='user.username')
    streak_days = serializers.IntegerField(source='current_streak')

    class Meta:
        model = UserProgress
        fields = ['user_id', 'name', 'points', 'solved_count', 'current_streak', 'streak_days']