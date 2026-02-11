from rest_framework import viewsets
from .models import Role, Permission

class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()

class PermissionViewSet(viewsets.ModelViewSet):
    queryset = Permission.objects.all()