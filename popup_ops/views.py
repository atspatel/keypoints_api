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
from .models import PopupData, PopupInstance, PopupCarouselMapping, PopupTag, Bbox
from utils.video_utils import create_video_obj_from_file, create_thumbnail_local_video, BASE_DIR

from media_ops.models import ImagesUrl, VideoUrl
from .serializers import MediaSerializers, AspectRatioSerializer
from .serializers import PopupInstanceSerializer, PopupInstanceMiniSerializer

from popup_ops.utils.media_utils import create_media_object
from popup_ops.utils.popup_utils import create_popup_instance_obj

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
            queryset = PopupInstance.objects.filter(id=q_id).first()
            data = PopupInstanceSerializer(queryset).data
            return Response({'status': True, "popup_data": data})

        queryset = PopupInstance.objects.all().order_by('-creation_date')
        if short:
            data = PopupInstanceMiniSerializer(queryset, many=True).data
        else:
            data = PopupInstanceSerializer(queryset, many=True).data

        return Response({'status': True, "popup_list": data})

    def post(self, request):
        popup = json.loads(request.data.get('popup', json.dumps({})))
        if(popup):
            popup_instance_obj = create_popup_instance_obj(popup)
            return Response({'status': True, "id": popup_instance_obj.id})
        return Response({'status': False, 'message': "popup data is empty"})
