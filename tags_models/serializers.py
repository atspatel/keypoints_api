from rest_framework import serializers
from .models import KeywordsTag, LanguageTag, KeypointsCategoryTag, KeypointsTopicTag

import re


class KeywordsTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = KeywordsTag
        fields = ('id', 'tag')

    def to_representation(self, value):
        return {"id": value.id, "tag": re.sub(r' ', '', value.tag)}


class LanguageTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = LanguageTag
        fields = ('id', 'tag', 'thumbnail_img')

    def to_representation(self, value):
        return {"id": value.id, "tag": value.tag, "thumbnail": value.thumbnail_img}


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = KeypointsCategoryTag
        fields = ('id', 'tag', 'thumbnail_img')

    def to_representation(self, value):
        return {"id": value.id, "tag": value.tag, "thumbnail": value.thumbnail_img}


class TopicSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField(read_only=True)
    logo_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = KeypointsTopicTag
        fields = ('id', 'name', 'followers', 'logo_url')

    def get_name(self, obj):
        return obj.tag

    def get_logo_url(self, obj):
        if obj.thumbnail_img:
            return obj.thumbnail_img
        else:
            video_posts = VideoPost.objects.filter(
                topics=obj).order_by('-views')
            for post in video_posts:
                if post.thumbnail_image:
                    return post.thumbnail_image
                    break
        return None
