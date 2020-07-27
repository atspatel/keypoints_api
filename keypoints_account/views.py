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
from .models import Creator, CreatorFollowerTable, KeywordFollowerTable, KeyPointsUserPreference
from tags_models.models import LanguageTag, KeypointsCategoryTag, KeywordsTag

from .serializers import UserMiniSerializer, UserSerializer

from tags_models.views import add_languages, add_categories, add_hashtags, add_topics

from utils.text_utils import text_to_query
from utils.image_upload import upload_profile_image, upload_image
from utils.video_utils import compress_and_hls_video, upload_file, BASE_DIR

import json
import os
import shutil
import hashlib
import logging
logging.getLogger().setLevel(logging.INFO)


def update_creator_follow_count(user_obj):
    creator_obj = Creator.objects.filter(
        user=user_obj).first()
    if creator_obj:
        follow_count = CreatorFollowerTable.objects.filter(
            followee=user_obj).count()
        creator_obj.followers = follow_count
        creator_obj.save()
    return creator_obj


class CreatorView(APIView):
    def get(self, request, suggestion_text=None):
        if(suggestion_text):
            user_list = Creator.objects.annotate(
                fullname=Concat('user__first_name',
                                Value(' '), 'user__last_name')
            ).filter(Q(fullname__icontains=suggestion_text) | Q(username__icontains=suggestion_text)).values_list('user', flat=True).distinct()
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
                'languages', json.dumps([])))
            categories = json.loads(request.data.get(
                'categories', json.dumps([])))

            creator_obj, _ = Creator.objects.update_or_create(
                user=user, defaults={"username": username, 'bio': about})
            creator_obj, _ = add_languages(
                languages, creator_obj, None)
            creator_obj, _ = add_categories(
                categories, creator_obj, None)

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
            elif category == 'hashtag':
                hashtag_obj = KeywordsTag.objects.filter(
                    id=qid).first() if qid else None
                if hashtag_obj:
                    follow_obj = KeywordFollowerTable.objects.filter(
                        follower=ann_obj, followee=hashtag_obj).first()
                    if follow_obj:
                        return Response({'status': True, "is_followed": True, 'id': hashtag_obj.id})
                    else:
                        return Response({'status': True, "is_followed": False, 'id': hashtag_obj.id})
                else:
                    return Response({'status': False, 'message': 'Hashtag Obj not found'})
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
            if category == "user":
                user_obj = User.objects.filter(
                    id=qid).first() if qid else None
                if user_obj:
                    if action == "follow":
                        follow_obj, _ = CreatorFollowerTable.objects.update_or_create(
                            follower=ann_obj, followee=user_obj, defaults={'is_logged_in': is_loggedIn})
                        update_creator_follow_count(user_obj)
                        return Response({'status': True, "is_followed": True, 'category': category, 'id': user_obj.id})
                    elif action == "unfollow":
                        follow_obj = CreatorFollowerTable.objects.filter(
                            follower=ann_obj, followee=user_obj).delete()
                        update_creator_follow_count(user_obj)
                        return Response({'status': True, "is_followed": False, 'category': category, 'id': user_obj.id})
                else:
                    return Response({'status': False, 'message': 'User Obj not found'})
            if category == "hashtag":
                hashtag_obj = KeywordsTag.objects.filter(
                    id=qid).first() if qid else None
                if hashtag_obj:
                    if action == "follow":
                        follow_obj, _ = KeywordFollowerTable.objects.update_or_create(
                            follower=ann_obj, followee=hashtag_obj, defaults={'is_logged_in': is_loggedIn})
                        return Response({'status': True, "is_followed": True, 'category': category, 'id': hashtag_obj.id})
                    elif action == "unfollow":
                        follow_obj = KeywordFollowerTable.objects.filter(
                            follower=ann_obj, followee=hashtag_obj).delete()
                        return Response({'status': True, "is_followed": False, 'category': category, 'id': hashtag_obj.id})
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

        categories_selected = prefrence_obj.categories.values_list(
            'id', flat=True) if prefrence_obj else []
        languages_selected = prefrence_obj.languages.values_list(
            'id', flat=True) if prefrence_obj else []

        categories_options = KeypointsCategoryTag.objects.all()
        languages_options = LanguageTag.objects.all()

        return Response({
            "status": True,
            "languages": {
                'options_list': [{"id": item.id,
                                  "tag": item.tag,
                                  "thumbnail": item.thumbnail_img,
                                  "selected": True if (item.id in languages_selected) else False}
                                 for item in languages_options],
            },
            "categories": {
                'options_list': [{"id": item.id,
                                  "tag": item.tag,
                                  "thumbnail": item.thumbnail_img,
                                  "selected": True if (item.id in categories_selected) else False}
                                 for item in categories_options],
            }
        })

    def post(self, request):
        ann_token = request.headers.get('Ann-Token', None)
        ann_obj = AnnonymousUserTable.objects.filter(id=ann_token).first()
        user = request.user

        categories = json.loads(request.data.get(
            'categories', json.dumps([])))
        languages = json.loads(request.data.get(
            'languages', json.dumps([])))

        categories_obj = KeypointsCategoryTag.objects.filter(id__in=categories)
        languages_obj = LanguageTag.objects.filter(id__in=languages)

        prefrence_obj, _ = KeyPointsUserPreference.objects.get_or_create(
            ann_user=ann_obj)

        prefrence_obj.categories.set(categories_obj)
        prefrence_obj.languages.set(languages_obj)

        logging.info(prefrence_obj.id)
        return Response({
            'status': True,
            'preference_id': prefrence_obj.id
        })


class UserNameCheck(APIView):
    def get(self, request, username=None):
        user = request.user
        if username and len(username) > 3:
            logging.info(username)
            creator_obj = Creator.objects.filter(
                username__iexact=username).first()
            if creator_obj and creator_obj.user != user:
                return Response({"status": False})
            return Response({'status': True})
        return Response({'status': False})

    def post(self, request):
        pass
