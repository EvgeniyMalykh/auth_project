from rest_framework.permissions import BasePermission
from .models import Role, BusinessElement, AccessRoleRule, UserRole


class IsAuthenticatedCustom(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and not getattr(request.user, "is_anonymous", False))


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        if not request.user or getattr(request.user, "is_anonymous", False):
            return False
        return UserRole.objects.filter(
            user=request.user, role__name="admin"
        ).exists()


class RbacPermission(BasePermission):
    """
    View должна иметь element_code.
    """

    def has_permission(self, request, view):
        user = request.user
        if not user or getattr(user, "is_anonymous", False):
            return False

        element_code = getattr(view, "element_code", None)
        if not element_code:
            return True

        try:
            element = BusinessElement.objects.get(code=element_code)
        except BusinessElement.DoesNotExist:
            return False

        rules = AccessRoleRule.objects.filter(
            role__role_users__user=user, element=element
        ).distinct()

        if not rules.exists():
            return False

        method = request.method.upper()

        def allowed_for_any_rule(check_owner=False):
            for rule in rules:
                if method in ("GET", "HEAD", "OPTIONS"):
                    if rule.read_all_permission:
                        return True
                    if rule.read_permission and not check_owner:
                        return True
                elif method == "POST":
                    if rule.create_permission:
                        return True
                elif method in ("PUT", "PATCH"):
                    if rule.update_all_permission:
                        return True
                    if rule.update_permission and not check_owner:
                        return True
                elif method == "DELETE":
                    if rule.delete_all_permission:
                        return True
                    if rule.delete_permission and not check_owner:
                        return True
            return False

        return allowed_for_any_rule(check_owner=False)

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user or getattr(user, "is_anonymous", False):
            return False

        element_code = getattr(view, "element_code", None)
        if not element_code:
            return True

        try:
            element = BusinessElement.objects.get(code=element_code)
        except BusinessElement.DoesNotExist:
            return False

        rules = AccessRoleRule.objects.filter(
            role__role_users__user=user, element=element
        ).distinct()

        if not rules.exists():
            return False

        method = request.method.upper()

        def is_owner(o) -> bool:
            owner_id = getattr(o, "owner_id", None) or getattr(
                o, "user_id", None
            ) or getattr(o, "owner", None)
            if hasattr(owner_id, "id"):
                return str(owner_id.id) == str(user.id)
            return str(owner_id) == str(user.id)

        owner = is_owner(obj)

        for rule in rules:
            if method in ("GET", "HEAD", "OPTIONS"):
                if rule.read_all_permission:
                    return True
                if rule.read_permission and owner:
                    return True
            elif method == "POST":
                if rule.create_permission:
                    return True
            elif method in ("PUT", "PATCH"):
                if rule.update_all_permission:
                    return True
                if rule.update_permission and owner:
                    return True
            elif method == "DELETE":
                if rule.delete_all_permission:
                    return True
                if rule.delete_permission and owner:
                    return True
        return False
