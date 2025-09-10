from django.db import models
from django.core.exceptions import ValidationError
from cloudinary_storage.storage import RawMediaCloudinaryStorage


class Document(models.Model):
    YEAR_CHOICES = [
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
    ]

    SEMESTER_CHOICES = [
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
        ('6', '6'),
        ('7', '7'),
        ('8', '8'),
    ]

    RESOURCE_TYPES = [
        ('Assignment', 'Assignment'),
        ('Learning Notes', 'Learning Notes'),
        ('Lab Manual', 'Lab Manual'),
        ('Resources', 'Resources'),
        ('Question Paper', 'Question Paper'),
        ('Project Report', 'Project Report'),
        ('Tutorial', 'Tutorial'),
        ('Presentation', 'Presentation'),
        ('Research Paper', 'Research Paper'),
    ]
    # Allowed file types with choices for the database
    FILE_TYPE_CHOICES = [
        ('pdf', 'PDF'),
        ('doc', 'DOC'),
        ('docx', 'DOCX'),
        ('txt', 'TXT'),
        ('ppt', 'PPT'),
        ('pptx', 'PPTX'),
        ('zip', 'ZIP'),
        ('jpg', 'JPG'),
        ('jpeg', 'JPEG'),
        ('png', 'PNG'),
        ('gif', 'GIF'),
        ('webp', 'WEBP'),
        ('xls', 'XLS'),
        ('xlsx', 'XLSX'),
        ('csv', 'CSV'),
    ]
    
    # Set of allowed extensions for validation
    ALLOWED_EXTENSIONS = {choice[0] for choice in FILE_TYPE_CHOICES}
    
    # Mapping from extension to normalized file type
    EXTENSION_TO_TYPE = {
        'pdf': 'pdf',
        'doc': 'doc',
        'docx': 'docx',
        'txt': 'txt',
        'ppt': 'ppt',
        'pptx': 'pptx',
        'zip': 'zip',
        'jpg': 'jpg',
        'jpeg': 'jpeg',
        'png': 'png',
        'gif': 'gif',
        'webp': 'webp',
        'xls': 'xls',
        'xlsx': 'xlsx',
        'csv': 'csv'
    }

    # Metadata fields
    title = models.CharField(max_length=500)
    name = models.CharField(max_length=500)
    description = models.TextField(blank=True, null=True)

    # File storage
    file = models.FileField(
        upload_to="documents/",
        storage=RawMediaCloudinaryStorage(resource_type="raw"),
        blank=True,
        null=True
    )
    file_url = models.URLField(max_length=500, blank=False)   # Cloudinary secure URL
    public_id = models.CharField(max_length=500, blank=True) # Cloudinary public_id

    # Classification
    file_type = models.CharField(max_length=500, choices=FILE_TYPE_CHOICES)
    college = models.CharField(max_length=500, default="General")
    branch = models.CharField(max_length=500, default="Default Branch")
    year = models.CharField(max_length=500, blank=True)
    semester = models.CharField(max_length=500, blank=True)
    subject = models.CharField(max_length=500, blank=True)
    resource_type = models.CharField(max_length=500, blank=True)

    # Timestamps
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "api_document"
        ordering = ["-uploaded_at"]

    def __str__(self):
        return self.title

    def clean(self):
        """
        Validate the model before saving
        """
        super().clean()
        
        # Validate file_type is set and valid
        if not self.file_type:
            raise ValidationError("File type is required.")
            
        if self.file_type not in self.ALLOWED_EXTENSIONS:
            raise ValidationError(
                f"File type '{self.file_type}' is not supported. "
                f"Allowed types: {', '.join(sorted(self.ALLOWED_EXTENSIONS))}"
            )
        
        # If we have a file, validate its extension matches the file_type
        if self.file and hasattr(self.file, 'name'):
            filename = self.file.name
            if '.' in filename:
                extension = filename.split('.')[-1].lower()
                normalized_extension = self.EXTENSION_TO_TYPE.get(extension, extension)
                
                if normalized_extension != self.file_type:
                    raise ValidationError(
                        f"File extension '.{extension}' does not match selected file type '{self.file_type}'."
                    )

    def save(self, *args, **kwargs):
        """
        Auto-populate file_url + public_id from Cloudinary.
        Ensure file_type is valid before saving.
        """
        # If file exists but file_url/public_id missing → set from Cloudinary
        if self.file and not self.file_url:
            try:
                self.file_url = self.file.url
            except Exception:
                pass
                
        if self.file and not self.public_id:
            try:
                self.public_id = getattr(self.file, "public_id", "")
            except Exception:
                pass

        # If file_type is not set but we have a file, try to detect it
        if not self.file_type and (self.file or self.file_url):
            self.detect_file_type()
            
        # Normalize file_type to lowercase
        if self.file_type:
            self.file_type = self.file_type.lower()

        # Run full validation before saving
        self.full_clean()
        
        super().save(*args, **kwargs)

    def detect_file_type(self):
        """
        Detect file type from filename or file_url and validate it.
        """
        filename = None
        if self.file and hasattr(self.file, "name"):
            filename = self.file.name
        elif self.file_url:
            filename = self.file_url

        if not filename or "." not in filename:
            raise ValidationError("Could not determine file type (no extension found).")

        extension = filename.split(".")[-1].lower()
        detected_type = self.EXTENSION_TO_TYPE.get(extension, extension)
        
        if detected_type not in self.ALLOWED_EXTENSIONS:
            raise ValidationError(
                f"File type '.{extension}' is not supported. "
                f"Allowed types: {', '.join(sorted(self.ALLOWED_EXTENSIONS))}"
            )
            
        self.file_type = detected_type
