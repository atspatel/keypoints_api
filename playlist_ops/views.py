from rest_framework.views import APIView
from rest_framework.response import Response
import json

import constants
import logging

import hashlib
import uuid


from .playlist_const import *
from .models import MediaInfo, Button, Title, PlaylistInfo
from .serializers import PlaylistSerializer


def is_valid_uuid(val):
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False


class PlaylistView(APIView):
    def get(self, request):
        p_id = request.GET.get('p_id', None)
        if(is_valid_uuid(p_id)):
            query = PlaylistInfo.objects.filter(id=p_id).first()
            if(query):
                data = PlaylistSerializer(query).data
                return Response({"status": True, "data": data})
            return Response({"status": False, "message": "Playlist id not found", "data": []})
        return Response({"status": False, "message": "Invalid UUID", "data": []})
