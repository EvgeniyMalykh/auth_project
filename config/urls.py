from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from core.views_auth import RegisterView, LoginView, LogoutView
from core.views_user import UserProfileView
from core.views_rbac_admin import (
    RoleViewSet,
    BusinessElementViewSet,
    AccessRoleRuleViewSet,
)
from core.views_mock import ProductsMockView, OrdersMockView

router = DefaultRouter()
router.register(r"admin/roles", RoleViewSet, basename="role")
router.register(r"admin/elements", BusinessElementViewSet, basename="element")
router.register(r"admin/rules", AccessRoleRuleViewSet, basename="access-rule")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/register/", RegisterView.as_view()),
    path("api/auth/login/", LoginView.as_view()),
    path("api/auth/logout/", LogoutView.as_view()),
    path("api/user/profile/", UserProfileView.as_view()),
    path("api/products/", ProductsMockView.as_view()),
    path("api/orders/", OrdersMockView.as_view()),
    path("api/", include(router.urls)),
]
