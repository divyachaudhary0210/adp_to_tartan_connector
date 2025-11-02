from rest_framework.permissions import BasePermission
from .models import AccessToken
from django.utils import timezone

class IsOAuthTokenValid(BasePermission):
    def has_permission(self, request, view):
        auth = request.META.get("HTTP_AUTHORIZATION", "")
        if not auth.startswith("Bearer "):
            return False
        token = auth.split(" ", 1)[1].strip()
        try:
            at = AccessToken.objects.get(token=token)
        except AccessToken.DoesNotExist:
            return False
        if at.expires_at < timezone.now():
            return False
        request.oauth_client = at.client
        return True
