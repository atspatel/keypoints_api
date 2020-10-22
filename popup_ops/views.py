from rest_framework.views import APIView
from rest_framework.response import Response
import json
import uuid

import constants
import logging

from .models import MediaButtonMapping, KpMediaInfo, AspectRatio
from .models import PopupData, PopupCarouselMapping, PopupTag, Bbox

from media_ops.models import ImagesUrl
from .serializers import MediaSerializers, AspectRatioSerializer

from utils.text_utils import text_to_query


def is_valid_uuid(val):
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False


class MediaView(APIView):
    def get(self, request):
        m_id = request.GET.get('m_id', None)
        if(is_valid_uuid(m_id)):
            query = KpMediaInfo.objects.filter(id=m_id).first()
            if(query):
                data = MediaSerializers(query).data
                return Response({"status": True, "data": data})
            return Response({"status": False, "message": "Playlist id not found", "data": []})
        return Response({"status": False, "message": "Invalid UUID", "data": []})

    def post(self, request):
        return Response({"status": True})


class AspectRatioView(APIView):
    def get(self, request):
        query = AspectRatio.objects.all().order_by('ratio')
        return Response({"status": True, "data": AspectRatioSerializer(query, many=True).data})

    def post(self, request):
        return Response({"status": True})


class PopupView(APIView):
    def get(self, request):
        return Response({'status': True})

    def post(self, request):
        popup = json.loads(request.data.get('popup', json.dumps({})))
        name = popup.get('name', None)
        id = popup.get('id', None)
        if(name):
            popup_info = popup.get('popup_info', {})

            popup_type = popup_info.get('type', None)
            aspect_ratio = popup_info.get('aspect_ratio', {})
            pauseVideo = popup_info.get('pauseVideo', False)
            showOverlayButton = popup_info.get('showOverlayButton', False)
            showCloseButton = popup_info.get('showCloseButton', True)
            inDuration = popup_info.get('inDuration', 1.0)
            bbox = popup_info.get(
                'bbox', {'top': 0.05, 'left': 0.05, 'width': 0.9, 'height': 0.9})

            popup_type_obj = PopupTag.objects.filter(
                key=text_to_query(popup_type)).first()
            aspect_ratio_obj = AspectRatio.objects.filter(
                id=aspect_ratio.get('id', None)).first() if aspect_ratio else None
            bbox_obj, _ = Bbox.objects.get_or_create(
                top=bbox.get('top', 0.05),
                left=bbox.get('left', 0.05),
                width=bbox.get('width', 0.9),
                height=bbox.get('height', 0.9)
            )
            popup_obj, _ = PopupData.objects.update_or_create(
                id=id, defaults=dict(name=name,
                                     popup_type=popup_type_obj,
                                     aspect_ratio=aspect_ratio_obj,
                                     bbox=bbox_obj,
                                     pause_video=pauseVideo,
                                     show_overlay_button=showOverlayButton,
                                     show_close_button=showCloseButton,
                                     in_duration=inDuration))
            data = popup.get('data', [])
            if(len(data) > 0):
                for i, media_data in enumerate(data):
                    kp_obj = None
                    if(media_data.get('media_type') == 'image'):
                        media = media_data.get('media', {})
                        url = media.get('src', None)
                        image_obj = ImagesUrl.objects.get(
                            image_url=url) if url else (None, None)
                        media_obj, _ = KpMediaInfo.objects.get_or_create(
                            image_url=image_obj,
                            defaults={
                                'media_type': constants.MEDIA_TYPE_IMAGE
                            }) if image_obj else (None, None)
                    PopupCarouselMapping.objects.update_or_create(
                        popup_id=popup_obj, media=media_obj, defaults={'index': i})
        return Response({'status': True, "id": popup_obj.id})
