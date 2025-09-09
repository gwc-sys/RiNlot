from rest_framework import serializers
from django.core.validators import FileExtensionValidator
from ..model.resourcemodels import Document

class DocumentSerializer(serializers.ModelSerializer):
    file_url = serializers.CharField(required=True, allow_blank=False)
    file_type = serializers.CharField(required=True, allow_blank=False)
    public_id = serializers.CharField(required=True, allow_blank=False)
    size = serializers.SerializerMethodField()
    upload_date = serializers.DateTimeField(source='uploaded_at', read_only=True)

    class Meta:
        model = Document
        fields = [
            'id', 'file', 'title', 'name', 'college', 'branch', 'year', 'semester',
            'subject', 'resource_type', 'description', 'file_type', 'file_url',
            'public_id', 'uploaded_at', 'upload_date', 'size'
        ]
        extra_kwargs = {
            'file': {
                'required': True,  # File is required
                'validators': [FileExtensionValidator(
                    allowed_extensions=['pdf', 'doc', 'docx', 'txt', 'ppt', 'pptx', 'zip',
                                      'jpg', 'jpeg', 'png', 'gif', 'webp', 'xls', 'xlsx', 'csv']
                )]
            },
            'title': {'required': True, 'allow_blank': False},
            'name': {'required': True, 'allow_blank': False},  # Name is required
            'college': {'required': True, 'allow_blank': False},
            'branch': {'required': True, 'allow_blank': False},
            'year': {'required': True, 'allow_blank': False},
            'semester': {'required': True, 'allow_blank': False},
            'subject': {'required': True, 'allow_blank': False},
            'resource_type': {'required': True, 'allow_blank': False},
            'description': {'required': True, 'allow_blank': False},  # Description is required
            'file_url': {'required': True, 'allow_blank': False},  # File URL is required
            'public_id': {'required': True, 'allow_blank': False},  # Public ID is required
        }
        read_only_fields = ['uploaded_at']

    def validate(self, data):
        """
        Comprehensive validation for the entire document
        """
        errors = {}
        
        # Validate file size if file is provided
        file = data.get('file')
        if file and hasattr(file, 'size'):
            max_size = 50 * 1024 * 1024  # 50MB
            if file.size > max_size:
                errors['file'] = [f'File size must be less than {max_size//1024//1024}MB']
        
        # Validate year and semester choices
        year = data.get('year')
        if year and year not in dict(Document.YEAR_CHOICES):
            errors['year'] = [f'Invalid year selection. Valid choices: {list(dict(Document.YEAR_CHOICES).keys())}']
        
        semester = data.get('semester')
        if semester and semester not in dict(Document.SEMESTER_CHOICES):
            errors['semester'] = [f'Invalid semester selection. Valid choices: {list(dict(Document.SEMESTER_CHOICES).keys())}']
        
        resource_type = data.get('resource_type')
        if resource_type and resource_type not in dict(Document.RESOURCE_TYPES):
            errors['resource_type'] = [f'Invalid resource type selection. Valid choices: {list(dict(Document.RESOURCE_TYPES).keys())}']
        
        # Validate required string fields are not empty
        required_string_fields = ['title', 'name', 'college', 'branch', 'subject', 'description', 'file_url', 'public_id']
        for field in required_string_fields:
            value = data.get(field)
            if value and isinstance(value, str) and not value.strip():
                errors[field] = [f'{field.replace("_", " ").title()} cannot be empty or whitespace only']
            elif not value:
                errors[field] = [f'{field.replace("_", " ").title()} is required']
        
        if errors:
            raise serializers.ValidationError(errors)
        
        return data

    # Removed get_file_url and get_file_type, now using CharField for both

    def get_size(self, obj):
        """
        Get file size in bytes
        """
        try:
            if obj.file:
                return obj.file.size
        except (AttributeError, ValueError, OSError):
            pass
        return 0

    def create(self, validated_data):
        """
        Handle document creation with all required fields
        """
        # Auto-detect file type if not provided
        file = validated_data.get('file')
        if file and not validated_data.get('file_type'):
            validated_data['file_type'] = self._detect_file_type_from_file(file)
        
        instance = super().create(validated_data)
        return instance

    def update(self, instance, validated_data):
        """
        Handle document updates
        """
        file = validated_data.get('file')
        if file and not validated_data.get('file_type'):
            validated_data['file_type'] = self._detect_file_type_from_file(file)
        
        return super().update(instance, validated_data)

    def _detect_file_type_from_file(self, file):
        """
        Detect file type from file object
        """
        if hasattr(file, 'name') and '.' in file.name:
            extension = file.name.split('.')[-1].lower()
            valid_types = [ft[0] for ft in Document.FILE_TYPE_CHOICES]
            return extension if extension in valid_types else 'unknown'
        return 'unknown'

    def to_internal_value(self, data):
        """
        Pre-process data before validation - strip whitespace from string fields
        """
        string_fields = ['title', 'name', 'college', 'branch', 'subject', 'description', 'file_url', 'public_id']
        for field in string_fields:
            if field in data and isinstance(data[field], str):
                data[field] = data[field].strip()
        
        return super().to_internal_value(data)