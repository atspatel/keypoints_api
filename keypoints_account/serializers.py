from rest_framework import serializers
from accounts.models import AnnonymousUserTable, User

from .models import Creator, CreatorFollowerTable
from tags_models.models import KeypointsCategoryTag, KeypointsTopicTag


import urllib.parse as urlparse
from urllib.parse import parse_qs


class UserMiniSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField(read_only=True)
    profile_pic = serializers.SerializerMethodField(read_only=True)
    follow_status = serializers.SerializerMethodField(read_only=True)
    followers = serializers.SerializerMethodField(read_only=True)

    def get_username(self, obj):
        if hasattr(obj, 'creator'):
            return obj.creator.username
        return None

    def get_profile_pic(self, obj):
        if obj.profile_pic:
            return obj.profile_pic.image_url
        return None

    def get_follow_status(self, obj):
        follow_status = 'unfollow'
        if(self.context and self.context.get('request', None)):
            ann_token = self.context['request'].headers.get('Ann-Token', None)
            ann_obj = AnnonymousUserTable.objects.filter(
                id=ann_token).first() if ann_token else None
            if ann_obj:
                if ann_obj.post_login_id == obj:
                    follow_status = 'self'
                else:
                    follow_status = 'follow' if CreatorFollowerTable.objects.filter(
                        follower=ann_obj, followee=obj).first() else 'unfollow'
        return follow_status

    def get_followers(self, obj):
        if hasattr(obj, 'creator'):
            return obj.creator.followers
        return 0

    class Meta:
        model = User
        fields = ('id', 'name', 'first_name',  'last_name', 'username',
                  'profile_pic', 'follow_status', 'followers')


class UserSerializer(UserMiniSerializer):
    # username = serializers.SerializerMethodField(read_only=True)
    bio = serializers.SerializerMethodField(read_only=True)

    categories_data = serializers.SerializerMethodField(read_only=True)
    languages_data = serializers.SerializerMethodField(read_only=True)

    # def get_username(self, obj):
    #     if hasattr(obj, 'creator'):
    #         return obj.creator.username
    #     return None

    def get_bio(self, obj):
        if hasattr(obj, 'creator'):
            return obj.creator.bio
        return None

    def get_categories_data(self, obj):
        if hasattr(obj, 'creator'):
            return [{'id': item.id, 'tag': item.tag} for item in obj.creator.categories.all()]
        return []

    def get_languages_data(self, obj):
        if hasattr(obj, 'creator'):
            return [{'id': item.id, 'tag': item.tag} for item in obj.creator.languages.all()]
        return []

    class Meta:
        model = User
        fields = ('id', 'name', 'username', 'bio', 'followers', 'first_name',  'last_name',
                  'profile_pic', 'categories_data', 'languages_data', 'follow_status')

# class CreatorMiniSerializer(serializers.ModelSerializer):
#     user_id = serializers.SerializerMethodField(read_only=True)
#     follow_status = serializers.SerializerMethodField(read_only=True)

#     class Meta:
#         model = Creator
#         fields = ('id', 'user_id', 'name', 'followers',
#                   'profile_pic', 'follow_status')

#     def get_user_id(self, obj):
#         return obj.user.id

#     def get_follow_status(self, obj):
#         follow_status = 'unfollow'
#         if(self.context and self.context.get('request', None)):
#             ann_token = self.context['request'].headers.get('Ann-Token', None)
#             ann_obj = AnnonymousUserTable.objects.filter(
#                 id=ann_token).first() if ann_token else None
#             if ann_obj:
#                 if ann_obj.post_login_id == obj.user:
#                     follow_status = 'self'
#                 else:
#                     follow_status = 'follow' if CreatorFollowerTable.objects.filter(
#                         follower=ann_obj, followee=obj.user).first() else 'unfollow'
#         return follow_status


# class CreatorSerializer(CreatorMiniSerializer):
#     categories_data = serializers.SerializerMethodField(read_only=True)
#     languages_data = serializers.SerializerMethodField(read_only=True)

#     class Meta:
#         model = Creator
#         fields = ('id', 'user_id', 'name', 'username', 'bio', 'followers',
#                   'profile_pic', 'categories_data', 'languages_data', 'follow_status')

#     def get_categories_data(self, obj):
#         return [{'id': item.id, 'tag': item.tag} for item in obj.categories.all()]

#     def get_languages_data(self, obj):
#         return [{'id': item.id, 'tag': item.tag} for item in obj.languages.all()]
