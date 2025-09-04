
from rest_framework import serializers
from ..model.resourcemodels import  Document


class DocumentSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    file_type = serializers.SerializerMethodField()
    size = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = "__all__"
        # If you want *all* fields read-only
        read_only_fields = [f.name for f in Document._meta.get_fields()]

    def get_file_url(self, obj):
        return obj.file.url if obj.file else None

    def get_file_type(self, obj):
        return obj.file.name.split('.')[-1].lower() if obj.file else None

    def get_size(self, obj):
        return obj.file.size if obj.file else None

    def validate_file(self, value):
        valid_extensions = ['pdf', 'doc', 'docx', 'txt', 'ppt', 'pptx']
        extension = value.name.split('.')[-1].lower()
        if extension not in valid_extensions:
            raise serializers.ValidationError(
                f"Unsupported file type. Allowed: {', '.join(valid_extensions)}"
            )
        return value

    def to_internal_value(self, data):
        print("\n[DocumentSerializer] Raw input data:", data)
        try:
            result = super().to_internal_value(data)
            print("[DocumentSerializer] Processed internal value:", result)
            return result
        except Exception as e:
            print("[DocumentSerializer] Error in to_internal_value:", str(e))
            raise

    def to_representation(self, instance):
        print("\n[DocumentSerializer] Converting instance to representation:", instance)
        try:
            result = super().to_representation(instance)
            print("[DocumentSerializer] Final representation:", result)
            return result
        except Exception as e:
            print("[DocumentSerializer] Error in to_representation:", str(e))
            raise

