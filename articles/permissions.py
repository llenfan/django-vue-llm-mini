from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow authors of an article to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions for any request (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions only for the author of the article
        return obj.author == request.user


class IsAuthorOrStaff(permissions.BasePermission):
    """
    Custom permission to allow authors or staff to edit articles.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions for any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions for author or staff
        return obj.author == request.user or request.user.is_staff


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Generic permission for any model with an 'owner' field.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions for any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions for owner only
        return getattr(obj, 'owner', None) == request.user