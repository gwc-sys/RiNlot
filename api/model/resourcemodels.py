from django.db import models
from cloudinary_storage.storage import RawMediaCloudinaryStorage
import os

class Document(models.Model):
    title = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    file = models.FileField(
        upload_to='documents/', 
        storage=RawMediaCloudinaryStorage(),
        blank=True,  # Make optional
        null=True    # Make optional
    )
    file_url = models.URLField(max_length=500, blank=True)
    public_id = models.CharField(max_length=255, blank=True)
    file_type = models.CharField(max_length=100, blank=True)
    college = models.CharField(max_length=100, default="General")
    branch = models.CharField(max_length=255, default="Default Branch")
    year = models.CharField(max_length=10, blank=True)
    semester = models.CharField(max_length=10, blank=True)
    subject = models.CharField(max_length=255, blank=True)
    resource_type = models.CharField(max_length=100, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'api_document'
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Auto-detect file type if not set
        if self.file and (not self.file_type or self.file_type == 'unknown'):
            self.detect_file_type()
        super().save(*args, **kwargs)

    def detect_file_type(self):
        """Detect file type from filename or file_url"""
        if self.file and hasattr(self.file, 'name'):
            filename = self.file.name
        elif self.file_url:
            filename = self.file_url
        else:
            self.file_type = 'unknown'
            return

        # Extract extension safely
        if '.' in filename:
            extension = filename.split('.')[-1].lower()
            
            # Map to consistent file types that frontend expects
            file_type_map = {
                'pdf': 'pdf',
                'doc': 'doc', 'docx': 'docx',
                'txt': 'txt',
                'ppt': 'ppt', 'pptx': 'pptx',
                'zip': 'zip',
                'jpg': 'jpg', 'jpeg': 'jpeg', 'png': 'png',
                'gif': 'gif', 'webp': 'webp',
                'xls': 'xls', 'xlsx': 'xlsx', 'csv': 'csv'
            }
            self.file_type = file_type_map.get(extension, extension)
        else:
            self.file_type = 'unknown'