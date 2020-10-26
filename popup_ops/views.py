from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

import json
import uuid
import os
import hashlib

import constants
import logging

from .models import MediaButtonMapping, KpMediaInfo, AspectRatio
from .models import PopupData, PopupCarouselMapping, PopupTag, Bbox
from utils.video_utils import create_video_obj_from_file, create_thumbnail_local_video, BASE_DIR

from media_ops.models import ImagesUrl, VideoUrl
from .serializers import MediaSerializers, AspectRatioSerializer
from .serializers import PopupDataSerializer, PopupDataMiniSerializer

from popup_ops.utils.media_utils import create_media_object

from utils.text_utils import text_to_query


def is_valid_uuid(val):
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False


class ResponseThen(Response):
    def __init__(self, data, then_callback, callback_args, request, **kwargs):
        super().__init__(data, **kwargs)
        self.callback_args = callback_args
        self.request = request
        self.then_callback = then_callback

    def close(self):
        super().close()
        self.then_callback(self.callback_args, self.request)


class KpMediaVideoView(APIView):
    def get(self, request):
        pass

    def post(self, request):
        video_file = request.data.get('media', None)
        media_id = request.data.get('media_id', None)
        name = request.data.get('name', None)

        media_obj = KpMediaInfo.objects.filter(id=media_id).first()
        if media_obj:
            return Response({
                'status': True,
                'isProcessing': False,
                "media_id": media_obj.id,
                "message": "already uploaded"
            })
        file_ext = video_file.name.rsplit('.', 1)[1]
        file_ext = file_ext if len(file_ext) > 0 else 'mp4'
        temp_filepath = os.path.join(
            BASE_DIR, "video_%s.%s" % (uuid.uuid4(), file_ext))
        video_hash = hashlib.sha256()
        with open(temp_filepath, 'wb+') as thefile:
            for chunk in video_file.chunks():
                video_hash.update(chunk)
                thefile.write(chunk)
        video_hash = video_hash.hexdigest()

        video_obj = VideoUrl.objects.filter(video_hash=video_hash).first()
        if(video_obj):
            os.remove(temp_filepath)
            media_obj = KpMediaInfo.objects.create(
                id=media_id if media_id else uuid.uuid4(),
                video_url=video_obj,
                media_type='video',
                name=name)
            return Response({
                "status": True,
                'isProcessing': False,
                "media_id": media_obj.id,
                "message": "video already uploaded, created media uploaded"
            })

        filepath = os.path.join(BASE_DIR, "video_%s.%s" %
                                (video_hash[:16], file_ext))
        os.rename(temp_filepath, filepath)

        def do_after(callback_args, request):
            filepath = callback_args['filepath']
            video_hash = callback_args['video_hash']
            media_id = callback_args['media_id']
            name = callback_args['name']

            thumbnail_image = request.data.get('thumbnail_image', None)
            if thumbnail_image == None:
                thumbnail_image = create_thumbnail_local_video(filepath)
            video_obj = create_video_obj_from_file(
                filepath, video_hash, thumbnail_image, user=None)
            media_obj = KpMediaInfo.objects.create(
                id=media_id,
                video_url=video_obj,
                media_type='video',
                name=name)
            os.remove(filepath)
            return True

        media_id = media_id if media_id else uuid.uuid4()
        callback_args = {
            "filepath": filepath,
            "video_hash": video_hash,
            "media_id": media_id,
            "name": name
        }
        data = {
            'media_id': media_id,
            'status': True,
            'isProcessing': True,
            'message': 'Video Uploaded, will be available soon.'
        }
        return ResponseThen(data, do_after, callback_args, request, status=status.HTTP_200_OK)


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
        media_info = json.loads(request.data.get('media_info', json.dumps({})))
        media_obj = create_media_object(media_info)
        return Response({"status": True, 'media_id': media_obj.id})


class AspectRatioView(APIView):
    def get(self, request):
        query = AspectRatio.objects.all().order_by('ratio')
        return Response({"status": True, "data": AspectRatioSerializer(query, many=True).data})

    def post(self, request):
        return Response({"status": True})


class PopupView(APIView):
    def get(self, request):
        q_id = request.GET.get('q_id', None)
        short = request.GET.get('short', False)
        if q_id:
            queryset = PopupData.objects.filter(id=q_id).first()
            data = PopupDataSerializer(queryset).data
            return Response({'status': True, "popup_data": data})
        queryset = PopupData.objects.all().order_by('-creation_date')
        if short:
            data = PopupDataMiniSerializer(queryset, many=True).data
        else:
            data = PopupDataSerializer(queryset, many=True).data
        return Response({'status': True, "popup_list": data})

    def post(self, request):
        popup = json.loads(request.data.get('popup', json.dumps({})))
        name = popup.get('name', None)
        id = popup.get('id', None)
        try:
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
            return Response({'status': False, 'message': "popup name is empty"})
        except:
            return Response({'status': False, 'message': "Some Error occured"})
