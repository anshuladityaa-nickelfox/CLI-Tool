from rest_framework import viewsets
from .models import Notification

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()