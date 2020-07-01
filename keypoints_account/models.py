from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator, URLValidator

from tags_models.models import KeywordsTag, LanguageTag
from tags_models.models import KeypointsCategoryTag, KeypointsTopicTag
from accounts.models import AnnonymousUserTable

import uuid
from django.conf import settings
User = settings.AUTH_USER_MODEL
# Create your models here.

url_validator = URLValidator(
    schemes=('http', 'https', 'ftp', 'ftps', 'rtsp', 'rtmp'))


class AbstractTimeClass(models.Model):
    creation_date = models.DateTimeField(default=timezone.now, blank=True)
    creation_date.editable = True
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Creator(AbstractTimeClass):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, unique=True, on_delete=models.CASCADE)
    # name = models.TextField()
    username = models.CharField(
        max_length=100, unique=True, null=True)
    bio = models.TextField(blank=True)
    # profile_pic = models.URLField(max_length=500, validators=[url_validator])
    rss_feed = models.URLField(max_length=500, validators=[
                               url_validator], unique=True, null=True, blank=True)
    channel_link = models.URLField(max_length=500, validators=[
                                   url_validator], unique=True, null=True, blank=True)

    categories = models.ManyToManyField(KeypointsCategoryTag, blank=True)
    languages = models.ManyToManyField(LanguageTag, blank=True)

    followers = models.IntegerField(default=0)
    num_of_posts = models.IntegerField(default=0)
    last_croned = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return "%s" % (self.user.name)


class FacebookInfo(AbstractTimeClass):
    display_name = models.CharField(max_length=200, null=True, blank=True)
    page_id = models.CharField(
        max_length=100, unique=True, null=True, blank=True)
    url = models.URLField(max_length=500, validators=[
        url_validator], unique=True, null=True)


class TwitterInfo(AbstractTimeClass):
    page_id = models.CharField(
        max_length=100, unique=True, null=True, blank=True)
    display_name = models.CharField(max_length=200, null=True, blank=True)
    url = models.URLField(max_length=500, validators=[
        url_validator], unique=True, null=True)


class YouTubeInfo(AbstractTimeClass):
    page_id = models.CharField(
        max_length=100, unique=True, null=True, blank=True)
    display_name = models.CharField(max_length=200, null=True, blank=True)
    url = models.URLField(max_length=500, validators=[
        url_validator], unique=True, null=True)


class WebsiteInfo(AbstractTimeClass):
    page_id = models.CharField(
        max_length=100, unique=True, null=True, blank=True)
    display_name = models.CharField(max_length=200, null=True, blank=True)
    url = models.URLField(max_length=500, validators=[
        url_validator], unique=True, null=True)


class CreatorProfile(AbstractTimeClass):
    creator = models.OneToOneField(Creator, related_name='%(class)s_profile',
                                   unique=True, on_delete=models.SET_NULL, null=True, blank=True)
    facebook_info = models.ForeignKey(
        FacebookInfo, blank=True, null=True, on_delete=models.CASCADE)
    twitter_info = models.ForeignKey(
        TwitterInfo, blank=True, null=True, on_delete=models.CASCADE)
    youtube_info = models.ForeignKey(
        YouTubeInfo, blank=True, null=True, on_delete=models.CASCADE)
    website_info = models.ForeignKey(
        WebsiteInfo, blank=True, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return "%s" % (self.creator)


class KeyPointsUserPreference(AbstractTimeClass):
    ann_user = models.OneToOneField(AnnonymousUserTable, related_name='%(class)s_pref',
                                    unique=True, on_delete=models.SET_NULL, null=True, blank=True)
    categories = models.ManyToManyField(KeypointsCategoryTag, blank=True)
    languages = models.ManyToManyField(LanguageTag, blank=True)


class CreatorFollowerTable(AbstractTimeClass):
    follower = models.ForeignKey(
        AnnonymousUserTable, related_name='%(class)s_follower', on_delete=models.CASCADE)
    followee = models.ForeignKey(
        User, related_name='%(class)s_followee', on_delete=models.CASCADE, null=True)
    is_logged_in = models.BooleanField(default=False)

    class Meta:
        unique_together = ["follower", "followee"]


class KeywordFollowerTable(AbstractTimeClass):
    follower = models.ForeignKey(
        AnnonymousUserTable, related_name='%(class)s_follower', on_delete=models.CASCADE)
    followee = models.ForeignKey(
        KeywordsTag, related_name='%(class)s_followee', on_delete=models.CASCADE, null=True)
    is_logged_in = models.BooleanField(default=False)

    class Meta:
        unique_together = ["follower", "followee"]
