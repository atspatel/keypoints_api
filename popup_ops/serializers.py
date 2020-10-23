from rest_framework import serializers
from django.conf import settings

import re
from constants import *

from .models import KpMediaInfo, MediaButtonMapping, ButtonData, ButtonInstance
from .models import Bbox, ActionDataMapping, AspectRatio
from .models import PopupData, PopupCarouselMapping, SeekToData, DownloadData, OpenUrlData


class AspectRatioSerializer(serializers.ModelSerializer):
    size = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = AspectRatio
        fields = ('id', 'ratio_s', 'ratio', 'image', 'size')

    def get_size(self, obj):
        return {"width": obj.width, 'height': obj.height}


class BboxSerializer(serializers.ModelSerializer):
    # bbox_info = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Bbox
        fields = ('id', 'top', 'left', 'width', 'height')

    def to_representation(self, obj):
        return {'top': obj.top, 'left': obj.left, 'width': obj.width, 'height': obj.height}


class PopupDataMiniSerializer(serializers.ModelSerializer):
    popup_info = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = PopupData
        fields = ('popup_info', )

    def get_popup_info(self, obj):
        return {
            "id": obj.id,
            "name": obj.name,
            "popupType": obj.popup_type.tag if obj.popup_type else None,
        }


class PopupDataSerializer(serializers.ModelSerializer):
    popup_info = serializers.SerializerMethodField(read_only=True)
    data = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = PopupData
        fields = ('popup_info', 'data')

    def get_popup_info(self, obj):
        return {
            "id": obj.id,
            "name": obj.name,
            "popupType": obj.popup_type.tag if obj.popup_type else None,
            "inDuration": obj.in_duration,
            "bbox": BboxSerializer(obj.bbox).data,
            "pauseVideo": obj.pause_video,
            "showOverlayButton": obj.show_overlay_button,
            "showCloseButton": obj.show_close_button
        }

    def get_data(self, obj):
        queryset = PopupCarouselMapping.objects.filter(
            popup_id=obj).order_by('index')
        button_list = [row.media for row in queryset if row.media]
        data = MediaSerializers(button_list, many=True).data
        return data
        return []


class SeekToDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = SeekToData
        fields = ('id', 'duration', 'toPlay')


class DownloadDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = DownloadData
        fields = ('id', 'url', 'filename')


class OpenUrlDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpenUrlData
        fields = ('id', 'url', 'inPopup')


class ActionSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    data = serializers.SerializerMethodField()

    class Meta:
        model = ActionDataMapping
        fields = ('id', 'type', 'data')

    def get_type(self, obj):
        return obj.action_id.tag if obj.action_id else None

    def get_data(self, obj):
        action_type = obj.action_id.tag if obj.action_id else None
        if action_type == "openPopup":
            return PopupDataSerializer(obj.popup_id).data
        elif action_type == "seekTo":
            return SeekToDataSerializer(obj.seekto_id).data
        elif action_type == "download":
            return DownloadDataSerializer(obj.download_id).data
        elif action_type == "openUrl":
            return OpenUrlDataSerializer(obj.openurl_id).data


class ButtonSerializer(serializers.ModelSerializer):
    class Meta:
        model = ButtonData
        fields = ('id', 'name', 'title', 'shape',
                  'background_img', 'style')


class ButtonInstanceSerializer(serializers.ModelSerializer):
    button_obj = serializers.SerializerMethodField(read_only=True)
    time = serializers.SerializerMethodField(read_only=True)
    pauseVideo = serializers.SerializerMethodField(read_only=True)
    action = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ButtonInstance
        fields = ('id', 'button_obj', 'time',
                  'pauseVideo', 'transform', 'action')

    def get_button_obj(self, obj):
        if obj.button_obj:
            return ButtonSerializer(obj.button_obj).data
        return None

    def get_time(self, obj):
        return {"start": obj.start, "end": obj.end}

    def get_pauseVideo(self, obj):
        return obj.pause_video_dur

    def get_action(self, obj):
        if obj.action_id:
            return ActionSerializer(obj.action_id).data
        return None


class MediaSerializers(serializers.ModelSerializer):
    media = serializers.SerializerMethodField(read_only=True)
    buttons = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = KpMediaInfo
        fields = ('id', 'media_type', 'name', 'media', 'buttons')

    def get_media(self, obj):
        if (obj.media_type == MEDIA_TYPE_VIDEO and obj.video_url):
            return {'src': obj.video_url.display_url, "thumbnail": obj.video_url.thumbnail_img}
        elif (obj.media_type == MEDIA_TYPE_AUDIO and obj.audio_url):
            return {'src': obj.audio_url.display_url, "thumbnail": obj.audio_url.thumbnail_img}
        elif (obj.media_type == MEDIA_TYPE_IMAGE and obj.image_url):
            return {'src': obj.image_url.display_url, "thumbnail": obj.image_url.thumbnail_img}
        return None

    def get_buttons(self, obj):
        queryset = MediaButtonMapping.objects.filter(
            media=obj).order_by('index')
        button_list = [row.button for row in queryset]
        data = ButtonInstanceSerializer(button_list, many=True).data
        return data
