from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from core.models import Tag, Ingredient, Recipe


class TagSerializer(ModelSerializer):
    """Serializer for Tag objects"""

    class Meta:
        model = Tag
        fields = ('id', 'name')
        read_only_fields = ('id',)


class IngredientSerializer(ModelSerializer):
    """Serializer for Ingredient objects"""

    class Meta:
        model = Ingredient
        fields = ('id', 'name')
        read_only_fields = ('id',)


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer to manage recipees objects"""
    ingredients = IngredientSerializer(many=True, read_only=False)
    tags = TagSerializer(many=True, read_only=False)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'ingredients', 'tags')
