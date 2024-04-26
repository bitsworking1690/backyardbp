from rest_framework import permissions
from utils.util import response_data_formating
from utils.enums import Enums


class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to access it.
    """

    message = response_data_formating(
        generalMessage='error',
        data=None,
        lang=None,
        error=['Not authorized to perform this action'],
    )

    def has_object_permission(self, request, view, obj):
        return obj == request.user


class IsAdminOrCRTSupervisor(permissions.BasePermission):
    """
    Grant access to only Admin & CRT Supervisior
    """
    
    message = response_data_formating(
        generalMessage='error',
        data=None,
        lang=None,
        error=['Not authorized to perform this action'],
    )

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            (request.user.user_type == Enums.ADMIN.value or request.user.user_type ==
             Enums.CRT_SUPERVISOR.value)
        )
