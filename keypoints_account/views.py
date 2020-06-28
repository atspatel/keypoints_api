# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import status

from django.db.models.functions import Concat
from django.db.models import Value, Count, Q
from django.core.paginator import Paginator, EmptyPage

from accounts.models import User, AnnonymousUserTable
from .models import Creator, CreatorFollowerTable, KeyPointsUserPreference
from tags_models.models import LanguageTag, KeypointsCategoryTag

from .serializers import UserMiniSerializer, UserSerializer

from tags_models.views import add_languages, add_categories, add_hashtags, add_topics

from utils.text_utils import text_to_query
from utils.image_upload import upload_profile_image, upload_image
from utils.video_utils import compress_and_hls_video, upload_file, BASE_DIR

import json
import os
import shutil
import hashlib


class CreatorView(APIView):
    def get(self, request, suggestion_text=None):
        if(suggestion_text):
            user_list = Creator.objects.annotate(
                fullname=Concat('user__first_name',
                                Value(' '), 'user__last_name')
            ).filter(fullname__icontains=suggestion_text).values_list('user', flat=True).distinct()
            queryset = User.objects.filter(id__in=user_list)
        else:
            user_id = request.GET.get('user_id', None)
            if(user_id):
                queryset = User.objects.filter(id=user_id)
                # queryset = Creator.objects.filter(user=user_obj)
            else:
                self_user = None if request.user.is_anonymous else request.user
                user_list = Creator.objects.exclude(user=self_user).values_list(
                    'user', flat=True).distinct()
                queryset = User.objects.filter(id__in=user_list)

        page_number = request.GET.get('p', 1)
        user_paginator = Paginator(queryset, 30)
        try:
            page_data = user_paginator.page(page_number)

        except EmptyPage as e:
            return Response({
                "status": False,
                "data": [],
                "message": "Empty Page Error",
                "next_p": None}, status=status.HTTP_200_OK)

        short = request.GET.get('short', None)
        if short:
            data = UserMiniSerializer(
                page_data, context={'request': request}, many=True).data
        else:
            data = UserSerializer(
                page_data, context={'request': request}, many=True).data
        next_p = page_data.next_page_number() if page_data.has_next() else None
        return Response({"status": True, "data": data, "next_p": next_p})

    def post(self, request):
        user = request.user
        if not user.is_anonymous:
            first_name = request.data.get('first_name', None)
            last_name = request.data.get('last_name', None)

            image = request.data.get('image', None)
            if (image):
                image_object = upload_profile_image(image)
            else:
                image_object = None

            user.first_name = first_name
            user.last_name = last_name
            user.profile_pic = image_object
            user.save()

            rss_feed = request.data.get('rss_feed', None)
            username = request.data.get('username', None)
            about = request.data.get('about', '')

            languages = json.loads(request.data.get(
                'languages', json.dumps({})))
            categories = json.loads(request.data.get(
                'categories', json.dumps({})))

            creator_obj, _ = Creator.objects.update_or_create(
                user=user, defaults={"username": username, 'bio': about})
            creator_obj, _ = add_languages(
                languages.values(), creator_obj, None)
            creator_obj, _ = add_categories(
                categories.values(), creator_obj, None)

            creator_obj.save()
            return Response({"status": True, "id": creator_obj.id, "user_name": user.name})
        return Response({"status": False})


class FollowView(APIView):
    # TODO:: check for creator object to user before follow
    def get(self, request):
        ann_token = request.headers.get('Ann-Token', None)
        ann_obj = AnnonymousUserTable.objects.filter(
            id=ann_token).first() if ann_token else None
        if ann_obj:
            category = request.GET.get('category', None)
            qid = request.GET.get('qid', None)
            if category == 'user':
                user_obj = User.objects.filter(
                    id=qid).first() if qid else None
                if user_obj:
                    follow_obj = CreatorFollowerTable.objects.filter(
                        follower=ann_obj, followee=user_obj).first()
                    if follow_obj:
                        return Response({'status': True, "is_followed": True, 'id': user_obj.id})
                    else:
                        return Response({'status': True, "is_followed": False, 'id': user_obj.id})
                else:
                    return Response({'status': False, 'message': 'User Obj not found'})
            else:
                return Response({'status': False, 'message': 'Category do not match'})
        else:
            return Response({'status': False, 'message': 'Request User Object not Found'})

    def post(self, request):
        ann_token = request.headers.get('Ann-Token', None)
        ann_obj = AnnonymousUserTable.objects.filter(
            id=ann_token).first() if ann_token else None
        if ann_obj:
            user = request.user
            is_loggedIn = False if user.is_anonymous else True
            category = request.data.get('category', None)
            qid = request.data.get('qid', None)
            action = request.data.get('action', None)
            print(category, qid, action)
            if category == "user":
                user_obj = User.objects.filter(
                    id=qid).first() if qid else None
                if user_obj:
                    if action == "follow":
                        follow_obj, _ = CreatorFollowerTable.objects.update_or_create(
                            follower=ann_obj, followee=user_obj, defaults={'is_logged_in': is_loggedIn})
                        return Response({'status': True, "is_followed": True, 'category': category, 'id': user_obj.id})
                    elif action == "unfollow":
                        follow_obj = CreatorFollowerTable.objects.filter(
                            follower=ann_obj, followee=user_obj).delete()
                        return Response({'status': True, "is_followed": False, 'category': category, 'id': user_obj.id})
                else:
                    return Response({'status': False, 'message': 'User Obj not found'})
            else:
                return Response({'status': False, 'message': 'Category do not match'})
        else:
            return Response({'status': False, 'message': 'Request User Object not Found'})


class KeyPointsPreferenceView(APIView):
    def get(self, request):
        ann_token = request.headers.get('Ann-Token', None)
        ann_obj = AnnonymousUserTable.objects.filter(id=ann_token).first()
        user = request.user

        prefrence_obj = KeyPointsUserPreference.objects.filter(
            ann_user=ann_obj).first()

        categories_selected = prefrence_obj.categories if prefrence_obj else KeypointsCategoryTag.objects.none()
        languages_selected = prefrence_obj.languages if prefrence_obj else LanguageTag.objects.none()

        categories_options = KeypointsCategoryTag.objects.all().exclude(
            id__in=categories_selected.values('id'))
        languages_options = LanguageTag.objects.all().exclude(
            id__in=languages_selected.values('id'))
        return Response({
            "status": True,
            "languages": {
                'options_list': {str(item.id): item.tag for item in languages_options},
                'selected_list': {str(item.id): item.tag for item in languages_selected.all()},
            },
            "categories": {
                'options_list': {str(item.id): item.tag for item in categories_options},
                'selected_list': {str(item.id): item.tag for item in categories_selected.all()},
            }
        })

    def post(self, request):
        ann_token = request.headers.get('Ann-Token', None)
        ann_obj = AnnonymousUserTable.objects.filter(id=ann_token).first()
        user = request.user

        categories = json.loads(request.data.get(
            'categories', json.dumps({}))).keys()
        languages = json.loads(request.data.get(
            'languages', json.dumps({}))).keys()

        categories_obj = KeypointsCategoryTag.objects.filter(id__in=categories)
        languages_obj = LanguageTag.objects.filter(id__in=languages)

        prefrence_obj, _ = KeyPointsUserPreference.objects.get_or_create(
            ann_user=ann_obj)

        prefrence_obj.categories.set(categories_obj)
        prefrence_obj.languages.set(languages_obj)

        print(prefrence_obj.id)
        return Response({
            'status': True,
            'preference_id': prefrence_obj.id
        })
