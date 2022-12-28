from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated

from accounts.authentication import TokenAuthentication
from core.models import Tag
from recipe import serializers


class TagViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    """Manage tags"""

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer

    def get_queryset(self):
        """Return objects that belongs to the aunthenticated user"""
        return self.queryset.filter(user=self.request.user).order_by("-name")
