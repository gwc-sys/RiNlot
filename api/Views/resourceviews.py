from django.shortcuts import render
from rest_framework import generics, status, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from ..model.resourcemodels import Document
from ..Serializers.resourceserializers import DocumentSerializer
import logging
import cloudinary.uploader
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from rest_framework.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination

logger = logging.getLogger(__name__)

class CustomPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

class ResourceListCreateView(generics.ListCreateAPIView):
    """List all resources or create new one with comprehensive validation"""
    queryset = Document.objects.all().order_by('-uploaded_at')
    serializer_class = DocumentSerializer
    parser_classes = [MultiPartParser, FormParser]
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['college', 'branch', 'year', 'semester', 'subject', 'resource_type', 'file_type']
    search_fields = ['title', 'name', 'description', 'college', 'branch', 'subject']
    ordering_fields = ['uploaded_at', 'title', 'college', 'branch']

    def list(self, request, *args, **kwargs):
        """Override list to include file URLs for frontend"""
        try:
            response = super().list(request, *args, **kwargs)
            # Ensure all documents have proper file_url in response
            for document_data in response.data.get('results', response.data):
                if 'file_url' not in document_data or not document_data['file_url']:
                    # Fallback to generate URL if missing
                    document = Document.objects.get(id=document_data['id'])
                    document_data['file_url'] = document.file_url if document.file_url else (
                        document.file.url if document.file else None
                    )
            return response
        except Exception as e:
            logger.error(f"Document list error: {str(e)}")
            return Response(
                {"error": "Failed to retrieve documents", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def create(self, request, *args, **kwargs):
        """Handle document creation with proper error handling"""
        try:
            return super().create(request, *args, **kwargs)
        except ValidationError as e:
            return Response(
                {"error": "Validation failed", "details": e.detail},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Document creation error: {str(e)}")
            return Response(
                {"error": "Document creation failed", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class FileUploadView(APIView):
    """Handle file uploads to Cloudinary with enhanced validation"""
    parser_classes = [MultiPartParser, FormParser]

    def validate_file(self, file):
        """Comprehensive file validation"""
        valid_extensions = [
            'pdf', 'doc', 'docx', 'txt', 'ppt', 'pptx', 'zip',
            'jpg', 'jpeg', 'png', 'gif', 'webp', 'xls', 'xlsx', 'csv'
        ]
        
        if not hasattr(file, 'name') or '.' not in file.name:
            raise ValidationError("Invalid file format")
        
        extension = file.name.split('.')[-1].lower()
        if extension not in valid_extensions:
            raise ValidationError(
                f"Unsupported file type. Allowed: {', '.join(valid_extensions)}"
            )
        
        max_size = 50 * 1024 * 1024
        if file.size > max_size:
            raise ValidationError(f"File size must be less than {max_size//1024//1024}MB")
        
        return True

    def post(self, request, format=None):
        """Handle file upload with comprehensive validation"""
        try:
            print('FILES:', request.FILES)
            if 'file' in request.FILES:
                print('File size:', request.FILES['file'].size)

            if 'file' not in request.FILES:
                return Response(
                    {"error": "No file provided"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            file = request.FILES['file']
            
            try:
                self.validate_file(file)
            except ValidationError as e:
                return Response(
                    {"error": "File validation failed", "details": {"file": [str(e)]}},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            filename = file.name
            file_extension = filename.split('.')[-1].lower() if '.' in filename else 'unknown'
            
            # Upload to Cloudinary
            upload_result = cloudinary.uploader.upload(
                file,
                resource_type='raw',
                folder='documents/',
                public_id=filename.rsplit('.', 1)[0]
            )

            # Reset file pointer for Django
            if hasattr(file, 'seek'):
                file.seek(0)

            # Prepare document data
            document_data = {
                'file': file,
                'title': request.data.get('title', ''),
                'name': request.data.get('name', ''),
                'description': request.data.get('description', ''),
                'file_url': upload_result['secure_url'],  # Store Cloudinary URL
                'public_id': upload_result['public_id'],
                'file_type': file_extension,
                'college': request.data.get('college', ''),
                'branch': request.data.get('branch', ''),
                'year': request.data.get('year', ''),
                'semester': request.data.get('semester', ''),
                'subject': request.data.get('subject', ''),
                'resource_type': request.data.get('resource_type', ''),
            }

            serializer = DocumentSerializer(data=document_data)
            if serializer.is_valid():
                document = serializer.save()  # This saves to the database!
                return Response(DocumentSerializer(document).data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            import traceback
            logger.error(f"File upload error: {str(e)}\n{traceback.format_exc()}")
            return Response(
                {
                    "error": "File upload failed",
                    "details": str(e),
                    "traceback": traceback.format_exc()
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class DocumentDetailView(APIView):
    """Get specific document with file URL for frontend"""
    
    def get(self, request, pk=None, format=None):
        try:
            if pk == 'all':
                # Return all documents with file URLs
                queryset = Document.objects.all().order_by('-uploaded_at')
                serializer = DocumentSerializer(queryset, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            
            elif pk == 'recent':
                # Return recent documents with file URLs
                queryset = Document.objects.all().order_by('-uploaded_at')[:10]
                serializer = DocumentSerializer(queryset, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            
            else:
                # Return specific document by ID with file URL
                try:
                    document = Document.objects.get(id=pk)
                    serializer = DocumentSerializer(document)
                    
                    # Ensure file_url is included in response
                    response_data = serializer.data
                    if not response_data.get('file_url') and document.file:
                        response_data['file_url'] = document.file.url
                    
                    return Response(response_data, status=status.HTTP_200_OK)
                except Document.DoesNotExist:
                    return Response(
                        {"error": "Document not found"},
                        status=status.HTTP_404_NOT_FOUND
                    )
            
        except Exception as e:
            logger.error(f"Document retrieval error: {str(e)}")
            return Response(
                {"error": "Document retrieval failed", "details": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class DocumentListView(generics.ListAPIView):
    """List documents with filtering and ensure file URLs are included"""
    serializer_class = DocumentSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['college', 'branch', 'year', 'semester', 'subject', 'resource_type', 'file_type']
    search_fields = ['title', 'name', 'description', 'college', 'branch', 'subject']
    ordering_fields = ['uploaded_at', 'title', 'college', 'branch']
    
    def get_queryset(self):
        queryset = Document.objects.all().order_by('-uploaded_at')
        
        # Apply filters
        college = self.request.query_params.get('college', None)
        branch = self.request.query_params.get('branch', None)
        year = self.request.query_params.get('year', None)
        semester = self.request.query_params.get('semester', None)
        subject = self.request.query_params.get('subject', None)
        resource_type = self.request.query_params.get('resource_type', None)
        file_type = self.request.query_params.get('file_type', None)
        
        if college:
            queryset = queryset.filter(college__icontains=college)
        if branch:
            queryset = queryset.filter(branch__icontains=branch)
        if year:
            queryset = queryset.filter(year=year)
        if semester:
            queryset = queryset.filter(semester=semester)
        if subject:
            queryset = queryset.filter(subject__icontains=subject)
        if resource_type:
            queryset = queryset.filter(resource_type__icontains=resource_type)
        if file_type:
            queryset = queryset.filter(file_type__icontains=file_type)
            
        return queryset

    def list(self, request, *args, **kwargs):
        """Override to ensure file URLs are included in response"""
        response = super().list(request, *args, **kwargs)
        
        # Ensure all documents have file URLs
        for document_data in response.data.get('results', []):
            if not document_data.get('file_url'):
                # If file_url is missing, try to get it from the document
                try:
                    document = Document.objects.get(id=document_data['id'])
                    document_data['file_url'] = document.file_url if document.file_url else (
                        document.file.url if document.file else None
                    )
                except Document.DoesNotExist:
                    document_data['file_url'] = None
        
        return response

class DocumentRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a specific document with file URL support"""
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    parser_classes = [MultiPartParser, FormParser]

    def retrieve(self, request, *args, **kwargs):
        """Retrieve document with ensured file URL"""
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            
            # Ensure file_url is included in response
            response_data = serializer.data
            if not response_data.get('file_url') and instance.file:
                response_data['file_url'] = instance.file.url
            
            return Response(response_data)
        except Exception as e:
            logger.error(f"Document retrieval error: {str(e)}")
            return Response(
                {"error": "Failed to retrieve document", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def update(self, request, *args, **kwargs):
        """Handle document updates with proper error handling"""
        try:
            return super().update(request, *args, **kwargs)
        except ValidationError as e:
            return Response(
                {"error": "Validation failed", "details": e.detail},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Document update error: {str(e)}")
            return Response(
                {"error": "Document update failed", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def destroy(self, request, *args, **kwargs):
        """Delete document and remove file from Cloudinary"""
        try:
            instance = self.get_object()
            
            # Delete file from Cloudinary if it exists
            if instance.public_id:
                try:
                    cloudinary.uploader.destroy(instance.public_id)
                    logger.info(f"Deleted file from Cloudinary: {instance.public_id}")
                except Exception as cloudinary_error:
                    logger.warning(f"Cloudinary deletion failed: {cloudinary_error}")
            
            # Delete the database record
            self.perform_destroy(instance)
            
            return Response(
                {"message": "Document deleted successfully"},
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            logger.error(f"Document deletion error: {str(e)}")
            return Response(
                {"error": "Document deletion failed", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class DocumentDeleteView(APIView):
    """Dedicated view for deleting documents from frontend"""
    
    def delete(self, request, pk, format=None):
        """Delete a specific document by ID"""
        try:
            # Get the document
            document = Document.objects.get(id=pk)
            
            # Delete from Cloudinary if public_id exists
            if document.public_id:
                try:
                    cloudinary.uploader.destroy(document.public_id)
                    logger.info(f"Deleted file from Cloudinary: {document.public_id}")
                except Exception as cloudinary_error:
                    logger.warning(f"Cloudinary deletion failed: {cloudinary_error}")
            
            # Delete from database
            document.delete()
            
            return Response(
                {"message": "Document deleted successfully", "deleted_id": pk},
                status=status.HTTP_200_OK
            )
            
        except Document.DoesNotExist:
            return Response(
                {"error": "Document not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Document deletion error: {str(e)}")
            return Response(
                {"error": "Document deletion failed", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class DocumentSearchView(generics.ListAPIView):
    """Advanced search functionality for documents with file URLs"""
    serializer_class = DocumentSerializer
    pagination_class = CustomPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'name', 'description', 'college', 'branch', 'subject', 'resource_type']

    def get_queryset(self):
        return Document.objects.all().order_by('-uploaded_at')

    def list(self, request, *args, **kwargs):
        """Override to ensure file URLs are included in search results"""
        response = super().list(request, *args, **kwargs)
        
        # Ensure all search results have file URLs
        for document_data in response.data.get('results', []):
            if not document_data.get('file_url'):
                try:
                    document = Document.objects.get(id=document_data['id'])
                    document_data['file_url'] = document.file_url if document.file_url else (
                        document.file.url if document.file else None
                    )
                except Document.DoesNotExist:
                    document_data['file_url'] = None
        
        return response