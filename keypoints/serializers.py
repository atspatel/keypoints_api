from rest_framework import serializers

from .models import VideoBuffer, VideoPost, VideoLike

from keypoints_account.serializers import UserMiniSerializer
import urllib.parse as urlparse
from urllib.parse import parse_qs


class VideoBufferSerializer(serializers.ModelSerializer):
    video_id = serializers.SerializerMethodField(read_only=True)
    languages_data = serializers.SerializerMethodField(read_only=True)
    topics_data = serializers.SerializerMethodField(read_only=True)
    categories_data = serializers.SerializerMethodField(read_only=True)
    hashtags_data = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = VideoBuffer
        fields = ('id', 'url', 'video_id', 'title', 'thumbnail_image',
                  'languages_data', 'topics_data', 'categories_data', 'hashtags_data', 'checked')

    def get_video_id(self, obj):
        url = obj.url
        video_ids = parse_qs(urlparse.urlparse(url).query).get('v', [])
        video_id = None
        if len(video_ids) > 0:
            video_id = video_ids[0]
        return video_id

    def get_languages_data(self, obj):
        return [item.tag for item in obj.languages.all()]

    def get_topics_data(self, obj):
        return [item.tag for item in obj.topics.all()]

    def get_categories_data(self, obj):
        return [item.tag for item in obj.categories.all()]

    def get_hashtags_data(self, obj):
        return [item.tag for item in obj.hashtags.all()]


class VideoPostSerializer(serializers.ModelSerializer):
    video_id = serializers.SerializerMethodField(read_only=True)
    languages_data = serializers.SerializerMethodField(read_only=True)
    topics_data = serializers.SerializerMethodField(read_only=True)
    categories_data = serializers.SerializerMethodField(read_only=True)
    hashtags_data = serializers.SerializerMethodField(read_only=True)
    user = serializers.SerializerMethodField(read_only=True)
    liked = serializers.SerializerMethodField(read_only=True)
    share_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = VideoPost
        fields = ('id', 'url', 'video_id', 'title', 'thumbnail_image',
                  'languages_data', 'topics_data', 'categories_data', 'hashtags_data', 'source',
                  'views', 'shared', 'user', 'liked', 'likes', 'share_url', 'external_urls')

    def get_video_id(self, obj):
        video_id = None
        if obj.source == "youtube":
            url = obj.url
            video_ids = parse_qs(urlparse.urlparse(url).query).get('v', [])
            video_id = None
            if len(video_ids) > 0:
                video_id = video_ids[0]
        return video_id

    def get_languages_data(self, obj):
        return [{'id': item.id, 'tag': item.tag} for item in obj.languages.all()]

    def get_topics_data(self, obj):
        return [{'id': item.id, 'tag': item.tag} for item in obj.topics.all()]

    def get_categories_data(self, obj):
        return [{'id': item.id, 'tag': item.tag} for item in obj.categories.all()]

    def get_hashtags_data(self, obj):
        return [{'id': item.id, 'tag': item.tag.replace(' ', '')} for item in obj.hashtags.all()]

    def get_user(self, obj):
        if (obj.creator):
            return UserMiniSerializer(obj.creator.user, context=self.context).data

    def get_liked(self, obj):
        if(self.context and self.context.get('request', None)):
            user = self.context['request'].user
            if user.is_anonymous:
                return False
            like_obj = VideoLike.objects.filter(
                user=user, video_id=obj).first()
            return True if like_obj else False

    def get_share_url(self, obj):
        if obj.source != 'youtube':
            return obj.compressed_url if obj.compressed_url else obj.original_url
        return obj.url
