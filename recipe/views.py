from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated

from accounts.authentication import TokenAuthentication
from core.models import Ingredient, Recipe, Tag
from recipe import serializers


class BaseRecipeAttrViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
):
    """Base viewset for user owned recipe attributes"""

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Returns objects that belongs to the authenticated user"""
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Creates an object owned by the authenticated user"""
        serializer.save(user=self.request.user)


class IngredientViewSet(BaseRecipeAttrViewSet):
    """Manage ingredients"""

    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer


class TagViewSet(BaseRecipeAttrViewSet):
    """Manage user tags"""

    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    """Manage recipes"""

    serializer_class = serializers.RecipeSerializer
    queryset = Recipe.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Retrieve the recipes that belongs to the authenticated user"""
        return self.queryset.filter(user=self.request.user)

    def get_serializer_class(self, *args, **kwargs):
        """Return appropriate serializer class"""
        if self.action == "retrieve":
            return serializers.RecipeDetailSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Creates an object owned by the authenticated user"""
        serializer.save(user=self.request.user)
