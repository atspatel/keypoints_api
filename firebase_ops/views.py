from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework import status


from .models import FcmTokenData
from accounts.models import AnnonymousUserTable
# Create your views here.


class FcmTokenView(APIView):
    def get(self, request):
        pass

    def post(self, request):
        fcmToken = request.data.get('fcmToken', None)
        ann_token = request.headers.get('Ann-Token', None)
        ann_obj = AnnonymousUserTable.objects.filter(id=ann_token).first()
        if ann_obj and fcmToken != None:
            obj, _ = FcmTokenData.objects.update_or_create(
                fcm_token=fcmToken, defaults={'ann_token': ann_obj})
            return Response({"status": True, "id": obj.id})
        return Response({"status": False, "id": None})
