from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import View

from .models import Task


class IsAuthenticatedCustom(BasePermission):
    def has_permission(self, request: Request, view: View) -> bool:
        return request.user and request.user.is_authenticated


class IsManagerOrAdmin(BasePermission):
    def has_permission(self, request: Request, view: View) -> bool:
        if request.user.role and request.user.role.name in ["Manager", "Administrator"]:
            return True
        return False


class IsTaskOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request: Request, view: View, obj: Task) -> bool:
        # Якщо користувач - адміністратор або власник таска, дозволяємо доступ
        if request.user.role and request.user.role.name in ["Administrator"]:
            return True
        if obj.assigned_to == request.user:
            return True
        return False


class IsUserOrAdminOrManager(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return user.is_authenticated and (user.role.name in ["Administrator", "Manager"] or user == view.get_object())
