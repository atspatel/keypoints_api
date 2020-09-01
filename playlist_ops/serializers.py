from rest_framework import serializers
from django.conf import settings
from .models import Title, Button, MediaInfo
from .models import PlaylistInfo, PlaylistMediaMapping

import re

from .playlist_const import *


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


class MediaInfoSerializer(serializers.ModelSerializer):
    button_info = serializers.SerializerMethodField(read_only=True)
    title_info = serializers.SerializerMethodField(read_only=True)
    language = serializers.SerializerMethodField(read_only=True)
    media_info = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = MediaInfo
        fields = ('id', 'button_info', 'title_info',
                  'media_type', 'media_info', 'language')

    def get_button_info(self, obj):
        if(obj.button):
            return ButtonSerializer(obj.button).data
        return None

    def get_title_info(self, obj):
        if(obj.title):
            return TitleSerializer(obj.title).data
        return None

    def get_language(self, obj):
        if(obj.language):
            return obj.language.tag.lower()
        return None

    def get_media_info(self, obj):
        if (obj.media_type == MEDIA_TYPE_VIDEO and obj.video_url):
            return {'src': obj.video_url.display_url, "thumbnail": obj.video_url.thumbnail_img}
        elif (obj.media_type == MEDIA_TYPE_AUDIO and obj.audio_url):
            return {'src': obj.audio_url.display_url, "thumbnail": obj.audio_url.thumbnail_img}
        return None


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
        media_list = [row.media for row in queryset]
        data = MediaInfoSerializer(media_list, many=True).data
        return data

    def get_secondary_list(self, obj):
        if(obj.secondary):
            queryset = PlaylistMediaMapping.objects.filter(
                playlist=obj, media_category=SECONDARY).order_by('index')
            media_list = [row.media for row in queryset]
            data = MediaInfoSerializer(media_list, many=True).data
            return data
        return []
