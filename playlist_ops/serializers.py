from rest_framework import serializers
from django.conf import settings
from .models import Title, Button
from .models import PlaylistInfo, PlaylistMediaMapping

from popup_ops.serializers import MediaSerializers
import re

from constants import *


def get_storage_url(url):
    return urljoin(settings.GS_STATIC_URL, url)


class ButtonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Button
        fields = ('id', 'name', 'action')


class TitleSerializer(serializers.ModelSerializer):
    language = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Title
        fields = ('id', "title_text", 'language')

    def get_language(self, obj):
        if(obj.language):
            return obj.language.tag.lower()
        return None


class PlaylistMappingSerializer(serializers.ModelSerializer):
    button_info = serializers.SerializerMethodField(read_only=True)
    title_info = serializers.SerializerMethodField(read_only=True)
    media_info = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = PlaylistMediaMapping
        fields = ('id', 'button_info', 'title_info', 'media_info')

    def get_button_info(self, obj):
        if(obj.button):
            return ButtonSerializer(obj.button).data
        return None

    def get_title_info(self, obj):
        if(obj.title):
            return TitleSerializer(obj.title).data
        return None

    def get_media_info(self, obj):
        return MediaSerializers(obj.kp_media).data


class PlaylistSerializer(serializers.ModelSerializer):
    primary_list = serializers.SerializerMethodField(read_only=True)
    secondary_list = serializers.SerializerMethodField(read_only=True)
    title_info = serializers.SerializerMethodField(read_only=True)
    language = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = PlaylistInfo
        fields = ('id', 'name', 'title_info', 'language',
                  'isSingleSecondary', 'primary', 'primary_list', 'secondary', 'secondary_list')

    def get_title_info(self, obj):
        if(obj.title):
            return TitleSerializer(obj.title).data
        return None

    def get_language(self, obj):
        if(obj.language):
            return obj.language.tag.lower()
        return None

    def get_primary_list(self, obj):
        queryset = PlaylistMediaMapping.objects.filter(
            playlist=obj, media_category=PRIMARY).order_by('index')
        data = PlaylistMappingSerializer(queryset, many=True).data
        return data

    def get_secondary_list(self, obj):
        if(obj.secondary):
            queryset = PlaylistMediaMapping.objects.filter(
                playlist=obj, media_category=SECONDARY).order_by('index')
            data = PlaylistMappingSerializer(queryset, many=True).data
            return data
        return []
