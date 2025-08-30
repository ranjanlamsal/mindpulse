"""
Custom permission classes for role-based access control.
"""
from rest_framework import permissions


class IsEmployee(permissions.BasePermission):
    """
    Permission that only allows employees to access the view.
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role == 'employee'
        )


class IsManager(permissions.BasePermission):
    """
    Permission that only allows managers to access the view.
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role in ['manager', 'admin']
        )


class IsAdmin(permissions.BasePermission):
    """
    Permission that only allows admins to access the view.
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role == 'admin'
        )


class IsManagerOrAdmin(permissions.BasePermission):
    """
    Permission that allows managers and admins to access the view.
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role in ['manager', 'admin']
        )


class IsOwnerOrManagerOrAdmin(permissions.BasePermission):
    """
    Permission that allows owners of the object, managers, and admins to access.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Check if user is the owner of the object
        if hasattr(obj, 'user') and obj.user == request.user:
            return True
        
        # Check if user is manager or admin
        return request.user.role in ['manager', 'admin']


class IsEmployeeForOwnData(permissions.BasePermission):
    """
    Permission that allows employees to only access their own data.
    Managers and admins can access all data.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Admins and managers can access any data
        if request.user.role in ['manager', 'admin']:
            return True
        
        # Employees can only access their own data
        if request.user.role == 'employee':
            # Check if the object belongs to the user
            if hasattr(obj, 'user') and obj.user == request.user:
                return True
            elif hasattr(obj, 'user_hash') and str(obj.user_hash) == str(request.user.hashed_id):
                return True
        
        return False