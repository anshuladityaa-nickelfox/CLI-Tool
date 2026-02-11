from rest_framework import viewsets
from .models import ErrorLog

class ErrorLogViewSet(viewsets.ModelViewSet):
    queryset = ErrorLog.objects.all()