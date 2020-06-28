from rest_framework import serializers
from .models import ImagesUrl


class ImagesUrlSerializer(serializers.ModelSerializer):
    thumbnail_uri = serializers.SerializerMethodField('get_thumbnail_uri')
    url = serializers.SerializerMethodField('get_url')

    def get_url(self, obj):
        return obj.image_url

    def get_thumbnail_uri(self, obj):
        return obj.thumbnail_img

    class Meta:
        model = ImagesUrl
        fields = ('id', 'image_hash', 'url', 'media_type', 'thumbnail_uri')
