from rest_framework import viewsets
from .models import Role, BusinessElement, AccessRoleRule
from .serializers import (
    RoleSerializer,
    BusinessElementSerializer,
    AccessRoleRuleSerializer,
)
from .permissions import IsAuthenticatedCustom, IsAdmin


class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticatedCustom, IsAdmin]


class BusinessElementViewSet(viewsets.ModelViewSet):
    queryset = BusinessElement.objects.all()
    serializer_class = BusinessElementSerializer
    permission_classes = [IsAuthenticatedCustom, IsAdmin]


class AccessRoleRuleViewSet(viewsets.ModelViewSet):
    queryset = AccessRoleRule.objects.select_related("role", "element").all()
    serializer_class = AccessRoleRuleSerializer
    permission_classes = [IsAuthenticatedCustom, IsAdmin]
