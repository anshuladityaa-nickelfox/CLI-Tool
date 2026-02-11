from rest_framework import viewsets
from .models import UploadedFile

class UploadedFileViewSet(viewsets.ModelViewSet):
    queryset = UploadedFile.objects.all()