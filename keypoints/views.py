# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticatedOrReadOnly
from rest_framework import status

from django.core.paginator import Paginator, EmptyPage

from accounts.models import User, AnnonymousUserTable
from keypoints_account.models import Creator, KeywordFollowerTable
from .models import VideoBuffer, VideoPost, VideoLike
from media_ops.models import VideoUrl
from tags_models.models import LanguageTag, KeywordsTag
from tags_models.models import KeypointsTopicTag, KeypointsCategoryTag

from .serializers import VideoBufferSerializer, VideoPostSerializer
from tags_models.serializers import LanguageTagSerializer
from tags_models.serializers import TopicSerializer, CategorySerializer

from tags_models.views import add_languages, add_categories, add_hashtags, add_topics
from utils.video_utils import create_video_obj_from_file, create_thumbnail_local_video, upload_file, BASE_DIR
from utils.image_upload import upload_image
from utils_slack.utils_slack import send_message

import json
import os

import hashlib
import uuid

import constants

def post_from_video_obj(video_obj, request):
    creator_obj = Creator.objects.filter(user=request.user).first()
    if not creator_obj:
        user = request.user
        username = "%s.%s"%(user.first_name.replace(' ', '').lower(), str(user.id)[:-4])
        creator_obj = Creator.objects.create(user=request.user, username=username)
    title = request.data.get('title', None)
    ext_url = request.data.get('url', '')
    ext_url = ext_url if len(ext_url) > 0 else None

    languages = json.loads(request.data.get(
        'languages', json.dumps([])))
    categories = json.loads(request.data.get(
        'categories', json.dumps([])))
    
    post_obj = VideoPost.objects.create(
                        video=video_obj, 
                        creator=creator_obj,
                        title=title,
                        external_urls=ext_url)
    lang_list = languages if isinstance(languages, list) else languages.values()
    cat_list = categories if isinstance(categories, list) else categories.values()
    post_obj, _= add_languages(lang_list, post_obj)
    post_obj, _= add_categories(cat_list, post_obj)
    post_obj.save()

    num_of_posts = max(creator_obj.num_of_posts, 0)
    creator_obj.num_of_posts = num_of_posts + 1
    creator_obj.save()
    print(post_obj.id, 'created ----------')
    message = "%s ::: %s ::: %s ::: %s"%(constants.MODE, post_obj.id, post_obj.creator, post_obj.title)
    send_message(constants.ALERT_UPLOAD_VIDEO, message)
    return post_obj


class ResponseThen(Response):
    def __init__(self, data, then_callback, filename, video_hash, request, **kwargs):
        super().__init__(data, **kwargs)
        self.filename = filename
        self.request = request
        self.video_hash = video_hash
        self.then_callback = then_callback

    def close(self):
        super().close()
        self.then_callback(self.filename, self.video_hash, self.request)

class VideoUploadView(APIView):
    def get(self, request):
        pass

    def post(self, request):
        user = request.user
        print(user)
        if user.is_anonymous:
            return Response({'status': False, 'message': 'AuthError'})
        
        video_file = request.data.get('video_file', None)
        file_ext = video_file.name.rsplit('.', 1)[1]
        file_ext = file_ext if len(file_ext) > 0 else 'mp4'
        temp_filepath = os.path.join(BASE_DIR, "video_%s.%s"%(uuid.uuid4(), file_ext))
        video_hash = hashlib.sha256()
        with open(temp_filepath, 'wb+') as thefile:
            for chunk in video_file.chunks():
                video_hash.update(chunk)
                thefile.write(chunk)
        video_hash = video_hash.hexdigest()
        
        video_obj = VideoUrl.objects.filter(video_hash=video_hash).first()
        if video_obj:
            os.remove(temp_filepath)
            post_obj = VideoPost.objects.filter(video=video_obj).first()
            if post_obj:
                return Response({'status': False, 'message': 'Video already exists', "id": post_obj.id})

            post_obj = post_from_video_obj(video_obj, request)
            return Response({'status': True, 'message': 'Post Created', "id": post_obj.id})

        filepath = os.path.join(BASE_DIR, "video_%s.%s"%(video_hash[:16], file_ext))
        os.rename(temp_filepath, filepath)

        def do_after(filepath, video_hash, request):
            thumbnail_image = request.data.get('thumbnail_image', None)
            if thumbnail_image == None:
                thumbnail_image = create_thumbnail_local_video(filepath)
            video_obj = create_video_obj_from_file(filepath, video_hash, thumbnail_image, user=None)
            post_obj = post_from_video_obj(video_obj, request)
            os.remove(filepath)
            return True

        data = {
                'status': True, 
                'message': 'Video Uploaded, will be available on timeline soon.'
                }
        return ResponseThen(data, do_after, filepath, video_hash, request, status=status.HTTP_200_OK)


class VideoPostView(APIView):
    def get(self, request, post_id = None):
        if(post_id):
            queryset=VideoPost.objects.filter(id = post_id)
        else:
            qcat=request.GET.get('qcat', None)
            qid=request.GET.get('qid', None)
            queryset=VideoPost.objects.none()
            if(qcat and qid):
                # TODO:: change first() to for many objs also
                if qcat == 'category':
                    obj=KeypointsCategoryTag.objects.filter(
                        id = qid).first()
                    queryset=VideoPost.objects.filter(
                        categories = obj) if obj else VideoPost.objects.none()
                elif qcat == 'topic':
                    obj=KeypointsTopicTag.objects.filter(
                        id = qid).first()
                    queryset=VideoPost.objects.filter(
                        topics = obj) if obj else VideoPost.objects.none()
                elif qcat == 'hashtag':
                    obj=KeywordsTag.objects.filter(
                        id = qid).first()
                    queryset=VideoPost.objects.filter(
                        hashtags = obj) if obj else VideoPost.objects.none()
                elif qcat == 'user_post':
                    user_obj=User.objects.filter(
                        id = qid).first()
                    obj=Creator.objects.filter(user = user_obj).first()
                    queryset=VideoPost.objects.filter(
                        creator = obj)
                elif qcat == 'discover':
                    queryset = VideoPost.objects.filter(title__icontains = qid)

            else:
                queryset=VideoPost.objects.all()
        # if(queryset):
        queryset=queryset.order_by('-creation_date')

        page_number = request.GET.get('p', 1)
        videoPost_paginator = Paginator(queryset, 20)
        try:
            page_data = videoPost_paginator.page(page_number)

        except EmptyPage as e:
            return Response({
                "status": False,
                "data": [],
                "message": "Empty Page Error",
                "next_p": None}, status=status.HTTP_200_OK)

        data=VideoPostSerializer(page_data, context = {'request': request}, many = True).data
        next_p = page_data.next_page_number() if page_data.has_next() else None

        return Response({'status': True, 'data': data, "next_p": next_p})
        # return Response({'status': False})

    def post(self, request):
        user=request.user
        url=request.data.get('url', None)
        if url:
            post_obj, _=VideoPost.objects.get_or_create(url = url)
            languages=json.loads(request.data.get(
                'languages', json.dumps([])))
            categories=json.loads(request.data.get(
                'categories', json.dumps([])))
            topics=json.loads(request.data.get(
                'topics', json.dumps([])))
            hashtags=json.loads(request.data.get(
                'hashtags', json.dumps([])))

            print('languages', languages)
            print('categories', categories)
            print('topics', topics)
            print('hashtags', hashtags)

            post_obj, _=add_languages(languages, post_obj)
            post_obj, _=add_categories(categories, post_obj)
            post_obj, _=add_topics(topics, post_obj)
            post_obj, _=add_hashtags(hashtags, post_obj)
            post_obj.save()
            print("-----------", post_obj.id)
            return Response({'id': post_obj.id, "status": True})
        return Response({"status": False})
    
    def delete(self, request, post_id=None):
        user = request.user
        if user.is_anonymous:
            return Response({'status': False, 'message': 'auth error'})
        if post_id:
            creator_obj = Creator.objects.filter(user = user).first()
            post_obj = VideoPost.objects.filter(id=post_id).first()
            if creator_obj and post_obj and post_obj.creator == creator_obj:
                delete_obj = post_obj.delete()
                return Response({'status': True, "id": post_id})
            else:
                return Response({'status': False, 'message': 'You are not allowed to delete'})
        else:
            return Response({'status': False, 'message': 'post_id not given'})


class VideoBufferView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        queryset=VideoBuffer.objects.filter(
            checked = False, deleted = False).order_by("-creation_date")
        data=VideoBufferSerializer(queryset, many = True).data
        return Response({"data": data, "status": True})

    def post(self, request):
        user=request.user
        buffer_id=request.data.get('id', None)
        if(buffer_id):
            buffer_obj=VideoBuffer.objects.filter(id = buffer_id).first()

            post_obj, _=VideoPost.objects.update_or_create(
                url = buffer_obj.url,
                defaults = {"title": buffer_obj.title,
                          "thumbnail_image": buffer_obj.thumbnail_image,
                          "duration": buffer_obj.duration,
                          "creator": buffer_obj.creator,
                          "creation_date": buffer_obj.creation_date})

            languages=json.loads(request.data.get(
                'languages', json.dumps([])))
            categories=json.loads(request.data.get(
                'categories', json.dumps([])))
            topics=json.loads(request.data.get(
                'topics', json.dumps([])))
            hashtags=json.loads(request.data.get(
                'hashtags', json.dumps([])))

            post_obj, buffer_obj=add_languages(
                languages, post_obj, buffer_obj)
            post_obj, buffer_obj=add_categories(
                categories, post_obj, buffer_obj)
            post_obj, buffer_obj=add_topics(
                topics, post_obj, buffer_obj)
            post_obj, buffer_obj=add_hashtags(
                hashtags, post_obj, buffer_obj)

            post_obj.save()

            buffer_obj.checked=True
            buffer_obj.save()
            return Response({'id': post_obj.id, "status": True})
        return Response({"status": False})

    def delete(self, request, buffer_id = None):
        if(buffer_id):
            buffer_obj=VideoBuffer.objects.filter(id = buffer_id).first()
            buffer_obj.deleted=True
            buffer_obj.checked=True
            buffer_obj.save()
            return Response({"status": True, "id": buffer_obj.id})
        return Response({"status": False})


class VideoLikeView(APIView):
    def get(self, request):
        pass

    def post(self, request):
        user = request.user
        if user.is_anonymous:
            return Response({'status': False, 'error': "LogInError"})

        video_id = request.data.get('video_id', None)
        video_obj = VideoPost.objects.filter(
            id=video_id).first() if video_id else None
        if video_obj:
            action = request.data.get('action', None)
            if action == 'like':
                like_obj, created = VideoLike.objects.get_or_create(
                    video_id=video_obj, user=user)
                if created:
                    video_obj.likes = video_obj.likes + 1
                    video_obj.save()
                return Response({'status': True, 'liked': True, 'likes': video_obj.likes, 'id': like_obj.id})
            else:
                like_obj = VideoLike.objects.filter(
                    video_id=video_obj, user=user)
                if like_obj:
                    like_obj.delete()

                    video_obj.likes = max(video_obj.likes - 1, 0)
                    video_obj.save()
                return Response({'status': True, 'liked': False, 'likes': video_obj.likes})
        return Response({'status': False, 'message': 'Video object not found'})


class VideoReshareView(APIView):
    def get(self, request):
        pass

    def post(self, request):
        ann_token = request.headers.get('Ann-Token', None)
        ann_obj = AnnonymousUserTable.objects.filter(
            id=ann_token).first() if ann_token else None
        video_id = request.data.get('video_id')
        video_obj = VideoPost.objects.filter(
            id=video_id).first() if video_id else None
        print(video_obj)
        return Response({'status': True})


class ThumbnailView(APIView):
    def get(self, request):
        pass

    def post(self, request):
        user = request.user
        image = request.data.get('image')
        image_url = None
        if image:
            image_object = upload_image(image, user=user)
            if image_object:
                image_url = image_object.thumbnail_img if image_object.thumbnail_img else image_object.image_url
        return Response({'status': True, "image_url": image_url})

class CategoryView(APIView):
    def get(self, request, suggestion_text=None):
        if (suggestion_text):
            queryset = KeypointsCategoryTag.objects.filter(
                tag__iregex=r"{0}".format(suggestion_text))
        else:
            queryset = KeypointsCategoryTag.objects.all()
        queryset = queryset.order_by('index')
        data = CategorySerializer(queryset, many=True).data
        return Response({"status": True, "category_options": data})

    def post(self, request):
        pass


class TopicView(APIView):
    def get(self, request, suggestion_text=None):
        if (suggestion_text):
            queryset = KeypointsTopicTag.objects.filter(
                tag__iregex=r"{0}".format(suggestion_text))
        else:
            qcat = request.GET.get('qcat', None)
            qid = request.GET.get('qid', None)
            queryset = None
            if(qcat and qid):
                # TODO:: change first() to for many objs also
                if qcat == 'category':
                    obj = KeypointsCategoryTag.objects.filter(
                        id=qid).first()
                    queryset = KeypointsTopicTag.objects.filter(
                        categories=obj).order_by('-creation_date') if obj else None
                elif qcat == 'trending':
                    queryset = KeypointsTopicTag.objects.all().order_by(
                        '-num_of_posts')
                elif qcat == 'user_topics':
                    user_obj = User.objects.filter(id=qid).first()
                    creator_obj = Creator.objects.filter(user=user_obj).first()
                    videos_obj = VideoPost.objects.filter(
                        creator=creator_obj)
                    topics = KeypointsTopicTag.objects.filter(
                        videopost__in=videos_obj).distinct()
                    print(topics, '-------')
                # elif qcat == 'user_post':
                #     queryset = KeypointsTopicTag.objects.all().order_by(
                #         '-num_of_posts')
            if queryset == None:
                queryset = KeypointsTopicTag.objects.all()

        data = TopicSerializer(
            queryset, context={'request': request}, many=True).data
        return Response({"status": True, "topic_data": data})

    def post(self, request):
        pass


class HashtagView(APIView):
    def get(self, request, suggestion_text=None):
        pass

    def post(self, request):
        pass


class OptionsView(APIView):
    def get(self, request):
        languages = LanguageTag.objects.all()
        languages_options = LanguageTagSerializer(languages, many=True).data
        
        categories = KeypointsCategoryTag.objects.all()
        categories_options = CategorySerializer(categories, many=True).data
        is_topic = request.GET.get('isTopic', False)
        topics_options = []
        if is_topic:
            topics = KeypointsTopicTag.objects.all()
            topics_options = [{"id": topic.id, "tag": topic.tag, "thumbnail": topic.thumbnail_img}
                              for topic in topics]
        return Response({"categories_options": categories_options,
                         "languages_options": languages_options,
                         "topics_options": topics_options})

    def post(self, request):
        pass


