from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from ..model.resourcemodels import  Document
from ..Serializers.resourceserializers import  DocumentSerializer
import logging
import cloudinary.uploader
import cloudinary.api
from django.shortcuts import get_object_or_404
import hashlib
from datetime import timedelta
from django.utils import timezone
from django.conf import settings

class ResourceListCreateView(generics.ListCreateAPIView):
    queryset = Document.objects.all().order_by('-uploaded_at')
    serializer_class = DocumentSerializer

class FileUploadView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request, format=None):
        try:
            if 'file' not in request.FILES:
                return Response(
                    {"error": "No file provided"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            file = request.FILES['file']
            upload_result = cloudinary.uploader.upload(
                file,
                resource_type='auto',
                folder='documents/',
                public_id=file.name.rsplit('.', 1)[0]
            )

            document = Document.objects.create(
                title=request.data.get('title', upload_result['original_filename']),
                name=request.data.get('name', upload_result['original_filename']),
                description=request.data.get('description', ''),
                file_url=upload_result['secure_url'],  # Store Cloudinary URL here
                public_id=upload_result['public_id'],
                file_type=file.name.split('.')[-1].lower(),
                college=request.data.get('college', ''),
                branch=request.data.get('branch', ''),
                resource_type=upload_result['resource_type']
            )

            serializer = DocumentSerializer(document)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            logging.error(f"Cloudinary upload error: {str(e)}")
            return Response(
                {"error": "File upload failed", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class DocumentDetailView(APIView):
    def get(self, request, pk, format=None):
        try:
            # Calculate the date one week ago
            one_week_ago = timezone.now() - timedelta(days=7)
            
            # Get all documents uploaded in the last week (no file_type filter)
            queryset = Document.objects.filter(
                uploaded_at__gte=one_week_ago
            )
            
            # Further filter if pk is provided
            if pk and pk == 'all':
                queryset = queryset.filter(name__icontains=pk)
            
            # Serialize the data
            serializer = DocumentSerializer(queryset, many=True)
            documents_data = serializer.data
            
            # Enhance each document with Cloudinary URL
            for doc in documents_data:
                if 'cloudinary_id' in doc:
                    doc['cloudinary_url'] = self.generate_cloudinary_url(doc['cloudinary_id'])
            
            return Response(documents_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logging.error(f"Document retrieval error: {str(e)}")
            return Response(
                {"error": "Document retrieval failed", "details": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def generate_cloudinary_url(self, public_id):
        """Generate Cloudinary URL from public_id"""
        return f"https://res.cloudinary.com/{settings.CLOUDINARY_STORAGE['CLOUD_NAME']}/raw/upload/{public_id}"

class DocumentListView(generics.ListAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer