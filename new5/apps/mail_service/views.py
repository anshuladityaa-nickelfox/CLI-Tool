from rest_framework import viewsets
from .models import Email

class EmailViewSet(viewsets.ModelViewSet):
    queryset = Email.objects.all()