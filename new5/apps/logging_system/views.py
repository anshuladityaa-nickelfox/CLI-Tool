from rest_framework import viewsets
from .models import LogEntry

class LogEntryViewSet(viewsets.ModelViewSet):
    queryset = LogEntry.objects.all()