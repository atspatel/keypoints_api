from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import status


from accounts.models import User, UserImagesUrl
from keypoints_account.models import Creator
from keypoints_account.serializers import UserMiniSerializer
from tags_models.models import KeypointsCategoryTag, LanguageTag

from keypoints.views import VideoUploadView

from utils.video_utils import create_video_obj_from_file, upload_file, BASE_DIR
import os
import uuid
import hashlib
import json
import re


class VideoPost(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        pass

    def post(self, request):
        creator = request.data.get('creator', None)
        user_obj = User.objects.filter(id=creator).first()
        if user_obj:
            request.user = user_obj

        videopost_obj = VideoUploadView()
        return videopost_obj.post(request)


class AdminCreatorView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        user_list = Creator.objects.all().values_list('user', flat=True).distinct()
        queryset = User.objects.filter(id__in=user_list)
        data = UserMiniSerializer(queryset, many=True).data
        return Response({"status": True, "data": data})

    def post(self, request):
        first_name = request.data.get('first_name', None)
        last_name = request.data.get('last_name', None)
        username = request.data.get('username', None)
        profile_pic = request.data.get('profile_pic', None)
        channel_url = request.data.get('channel_url', None)
        about = request.data.get('about', None)
        languages = json.loads(request.data.get(
            'languages', json.dumps([])))
        categories = json.loads(request.data.get(
            'categories', json.dumps([])))

        if channel_url:
            creator_obj = Creator.objects.filter(
                channel_link=channel_url).first()
            if creator_obj:
                return Response({'status': False, 'message': "creator with channel url already exists"})

        user_count = User.objects.all().count()
        while True:
            phone_number = int("1%09d" % (user_count))
            user_obj = User.objects.filter(phone=phone_number).first()
            if user_obj:
                user_count += 1
            else:
                break

        hash_val = hashlib.md5(profile_pic.encode('utf-8')).hexdigest()
        profile_pic, _ = UserImagesUrl.objects.get_or_create(image_url=profile_pic,
                                                             image_hash=hash_val)
        user_obj, _ = User.objects.update_or_create(phone=phone_number,
                                                    defaults={
                                                        "first_name": first_name,
                                                        "last_name": last_name,
                                                        "profile_pic": profile_pic
                                                    })
        creator_obj, _ = Creator.objects.update_or_create(
            channel_link=channel_url, defaults={'user': user_obj,
                                                'username': username.replace(' ', ''),
                                                'is_active': True})

        for category in categories:
            key = re.sub("[^a-z]+", "", category.lower())
            category_obj = KeypointsCategoryTag.objects.filter(
                key=key).first()
            if category_obj:
                creator_obj.categories.add(category_obj)
            else:
                print("Category not found :: ", category)

        for lang in languages:
            key = re.sub("[^a-z]+", "", lang.lower())
            language_obj = LanguageTag.objects.filter(key=key).first()
            if language_obj:
                creator_obj.languages.add(language_obj)
            else:
                print("language not found :: ", lang)

        creator_obj.save()
        return Response({"status": True,
                         "message": 'User created successfully. Refresh page to apply changes',
                         "id": creator_obj.id})
