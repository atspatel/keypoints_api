from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework import status

from .models import ActivityOps


class ActivityView(APIView):
    def get(self, request):
        return Response({'status': True})

    def post(self, request):
        activity = request.data.get('activity', None)
        if activity:
            video_id = request.data.get('video_id', None)
            button_id = None
            if activity == 'click':
                button_id = request.data.get('button_id', None)
            activity_obj = ActivityOps.objects.create(
                activity=activity, video_id=video_id, button_id=button_id)

        activity_id = activity_obj.id if activity_obj else None
        print('Video_activity :: ', activity_id)
        return Response({'status': True, "activity_id": activity_id})
