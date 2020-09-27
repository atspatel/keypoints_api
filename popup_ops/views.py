from rest_framework.views import APIView
from rest_framework.response import Response
import json
import uuid

import constants
import logging

from .models import MediaButtonMapping, KpMediaInfo
from .serializers import MediaSerializers


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
        pass
