from rest_framework import serializers
from ..model.resourcemodels import Document
import os

class DocumentSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    file_type = serializers.SerializerMethodField()
    size = serializers.SerializerMethodField()
    upload_date = serializers.DateTimeField(source='uploaded_at', read_only=True)

    class Meta:
        model = Document
        fields = [
            'id', 'title', 'name', 'description', 'file', 'file_url',
            'public_id', 'file_type', 'college', 'branch', 'resource_type',
            'uploaded_at', 'upload_date', 'size'
        ]
        read_only_fields = ['file_url', 'public_id', 'uploaded_at']

    def get_file_url(self, obj):
        """Get file URL - prefer file_url field, fallback to file.url"""
        if obj.file_url:
            return obj.file_url
        return obj.file.url if obj.file else None

    def get_file_type(self, obj):
        """Get file type - ensure it matches frontend expectations"""
        # Use the file_type field if available
        if obj.file_type:
            return obj.file_type.lower()
        
        # Fallback: extract from filename
        if obj.file and hasattr(obj.file, 'name'):
            filename = obj.file.name
            if '.' in filename:
                extension = filename.split('.')[-1].lower()
                # Map to frontend-supported types
                frontend_types = ['pdf', 'doc', 'docx', 'txt', 'ppt', 'pptx', 'zip', 
                                 'jpg', 'jpeg', 'png', 'gif', 'webp']
                return extension if extension in frontend_types else 'unknown'
        
        # Final fallback: extract from file_url
        if obj.file_url and '.' in obj.file_url:
            extension = obj.file_url.split('.')[-1].lower()
            return extension
        
        return 'unknown'

    def get_size(self, obj):
        """Get file size in bytes"""
        try:
            if obj.file:
                return obj.file.size
        except:
            pass
        return 0

    def validate_file(self, value):
        """Validate uploaded file types"""
        valid_extensions = ['pdf', 'doc', 'docx', 'txt', 'ppt', 'pptx', 'zip', 
                           'jpg', 'jpeg', 'png', 'gif', 'webp']
        
        if hasattr(value, 'name') and '.' in value.name:
            extension = value.name.split('.')[-1].lower()
            if extension not in valid_extensions:
                raise serializers.ValidationError(
                    f"Unsupported file type. Allowed: {', '.join(valid_extensions)}"
                )
        return value

    def create(self, validated_data):
        """Handle file upload and type detection during creation"""
        instance = super().create(validated_data)
        
        # Ensure file_type is set
        if instance.file and not instance.file_type:
            instance.detect_file_type()
            instance.save()
            
        return instance