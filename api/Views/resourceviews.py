from django.shortcuts import render
from rest_framework import generics, status
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

logger = logging.getLogger(__name__)

class ResourceListCreateView(generics.ListCreateAPIView):
    """List all resources or create new one"""
    queryset = Document.objects.all().order_by('-uploaded_at')
    serializer_class = DocumentSerializer
    parser_classes = [MultiPartParser, FormParser]

class FileUploadView(APIView):
    """Handle file uploads to Cloudinary"""
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, format=None):
        try:
            if 'file' not in request.FILES:
                return Response(
                    {"error": "No file provided"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            file = request.FILES['file']
            filename = file.name
            
            # Extract file extension
            file_extension = filename.split('.')[-1].lower() if '.' in filename else 'unknown'
            
            # Upload to Cloudinary
            upload_result = cloudinary.uploader.upload(
                file,
                resource_type='raw',  # Use 'raw' for documents
                folder='documents/',
                public_id=filename.rsplit('.', 1)[0]  # Remove extension from public_id
            )

            # Create document instance
            document_data = {
                'title': request.data.get('title', upload_result['original_filename']),
                'name': request.data.get('name', upload_result['original_filename']),
                'description': request.data.get('description', ''),
                'file_url': upload_result['secure_url'],
                'public_id': upload_result['public_id'],
                'file_type': file_extension,
                'college': request.data.get('college', ''),
                'branch': request.data.get('branch', ''),
                'resource_type': request.data.get('resource_type', 'Document'),
                'file': file  # Keep the file for size detection
            }

            # Use serializer for validation and creation
            serializer = DocumentSerializer(data=document_data)
            if serializer.is_valid():
                document = serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(
                    {"error": "Validation failed", "details": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )

        except Exception as e:
            logger.error(f"File upload error: {str(e)}")
            return Response(
                {"error": "File upload failed", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class DocumentDetailView(APIView):
    """Get specific document or filtered list"""
    
    def get(self, request, pk=None, format=None):
        try:
            if pk == 'all':
                # Return all documents
                queryset = Document.objects.all().order_by('-uploaded_at')
            elif pk == 'recent':
                # Return the 10 most recently uploaded documents
                queryset = Document.objects.all().order_by('-uploaded_at')[:10]
            else:
                # Return specific document by ID
                queryset = Document.objects.filter(id=pk)
                if not queryset.exists():
                    return Response(
                        {"error": "Document not found"},
                        status=status.HTTP_404_NOT_FOUND
                    )

            if pk in ['all', 'recent']:
                serializer = DocumentSerializer(queryset, many=True)
            else:
                serializer = DocumentSerializer(queryset, many=False)
                
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Document retrieval error: {str(e)}")
            return Response(
                {"error": "Document retrieval failed", "details": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class DocumentListView(generics.ListAPIView):
    """List all documents with filtering support"""
    serializer_class = DocumentSerializer
    
    def get_queryset(self):
        queryset = Document.objects.all().order_by('-uploaded_at')
        
        # Add filters from query parameters..
        college = self.request.query_params.get('college', None)
        branch = self.request.query_params.get('branch', None)
        resource_type = self.request.query_params.get('resource_type', None)
        
        if college:
            queryset = queryset.filter(college__icontains=college)
        if branch:
            queryset = queryset.filter(branch__icontains=branch)
        if resource_type:
            queryset = queryset.filter(resource_type__icontains=resource_type)
            
        return queryset

# Add this view for individual document operations
class DocumentRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a specific document"""
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    parser_classes = [MultiPartParser, FormParser]