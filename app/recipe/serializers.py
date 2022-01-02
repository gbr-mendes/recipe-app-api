from rest_framework.serializers import ModelSerializer

from core.models import Tag


class TagSerializer(ModelSerializer):
    """Serializer for Tag objects"""

    class Meta:
        model = Tag
        fields = ('id', 'name')
        read_only_fields = ('id',)
