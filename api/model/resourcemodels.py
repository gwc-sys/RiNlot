from django.db import models
from cloudinary_storage.storage import RawMediaCloudinaryStorage
from ..model.User import User, SessionCode

class Document(models.Model):
    title = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to='documents/', storage=RawMediaCloudinaryStorage())
    file_url = models.URLField(max_length=500, blank=True)
    public_id = models.CharField(max_length=255, blank=True)
    file_type = models.CharField(max_length=100, blank=True)
    college = models.CharField(max_length=100, default="General")
    branch = models.CharField(max_length=255, default="Default Branch")
    resource_type = models.CharField(max_length=100, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'api_document'  # Explicitly set table name

    def __str__(self):
        return self.title