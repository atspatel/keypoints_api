from rest_framework.views import APIView
from rest_framework.response import Response

import logging
import uuid

from constants import storage_dir
from utils.image_upload import upload_image


class ImageView(APIView):
    def get(self, request):
        pass

    def post(self, request):
        image = request.data.get('image')
        image_url = None
        if image:
            image_object = upload_image(image, user=None)
            if image_object:
                image_url = image_object.image_url
        return Response({'status': True, "image_url": image_url})
