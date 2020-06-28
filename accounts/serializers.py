from rest_framework import serializers

from .models import User, AnnonymousUserTable


class UserName(serializers.RelatedField):
    def to_representation(self, value):
        is_followed = False
        user_self = False

        if value.profile_pic:
            image_url = value.profile_pic.image_url
        else:
            image_url = "https://encrypted-tbn0.gstatic.com/images?q=tbn%3AANd9GcSDgTNKTeE985pM29w_MVlLv6Q6zXuK8qHKq4O0pcB_aWH4JbQV"

        if value.last_name:
            name = "%s %s" % (value.first_name, value.last_name)
        else:
            name = value.first_name
        return {"id": value.id,
                "name": name,
                "profile_pic": image_url,
                "is_followed": is_followed,
                "user_self": user_self}


class UserShortInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "user_name")

    def to_representation(self, value):
        if value.profile_pic:
            image_url = value.profile_pic.image_url
        else:
            image_url = "https://encrypted-tbn0.gstatic.com/images?q=tbn%3AANd9GcSDgTNKTeE985pM29w_MVlLv6Q6zXuK8qHKq4O0pcB_aWH4JbQV"

        if value.last_name:
            name = "%s %s" % (value.first_name, value.last_name)
        else:
            name = value.first_name
        return {value.id: {"id": value.id,
                           "name": name,
                           "profile_pic": image_url}}


class UserSerializer(serializers.ModelSerializer):
    profile_pic = serializers.SerializerMethodField(read_only=True)
    follower = serializers.SerializerMethodField(read_only=True)
    posts = serializers.SerializerMethodField(read_only=True)
    is_followed = serializers.SerializerMethodField(read_only=True)
    user_self = serializers.SerializerMethodField(read_only=True)

    def get_profile_pic(self, obj):
        if obj.profile_pic:
            return obj.profile_pic.image_url
        return None

    def get_follower(self, obj):
        return 0

    def get_posts(self, obj):
        return 0

    def get_is_followed(self, obj):
        return False

    def get_user_self(self, obj):
        ann_token = self.context['request'].headers.get('Ann-Token', None)
        if ann_token:
            ann_obj = AnnonymousUserTable.objects.filter(id=ann_token).first()
            if ann_obj and ann_obj.post_login_id == obj:
                return True
        return False

    class Meta:
        model = User
        fields = ('id', 'name', 'profile_pic', "follower",
                  "posts", "is_followed", "user_self")


class UserBioSerializer(serializers.ModelSerializer):
    profile_pic = serializers.SerializerMethodField(read_only=True)

    def get_profile_pic(self, obj):
        if obj.profile_pic:
            return obj.profile_pic.image_url
        return None

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'profile_pic')
