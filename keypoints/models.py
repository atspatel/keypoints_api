from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator, URLValidator

from accounts.models import AnnonymousUserTable, User
from keypoints_account.models import Creator
from tags_models.models import KeywordsTag, LanguageTag
from tags_models.models import KeypointsCategoryTag, KeypointsTopicTag
from media_ops.models import VideoUrl


import uuid
from django.conf import settings

# Create your models here.

url_validator = URLValidator(
    schemes=('http', 'https', 'ftp', 'ftps', 'rtsp', 'rtmp'))


class AbstractTimeClass(models.Model):
    creation_date = models.DateTimeField(default=timezone.now, blank=True)
    creation_date.editable = True
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class VideoPost(AbstractTimeClass):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # video_obj = models.ForeignKey(VideoUrl, on_delete=models.CASCADE)

    # TODO:: Remove this and change Views and Serializers
    video_hash = models.CharField(
        max_length=300, unique=True, null=True, blank=True)
    url = models.URLField(max_length=500, validators=[
                          url_validator], unique=True)
    original_url = models.URLField(max_length=500, validators=[
        url_validator], unique=True, blank=True, null=True)
    compressed_url = models.URLField(max_length=500, validators=[
        url_validator], unique=True, blank=True, null=True)
    thumbnail_image = models.URLField(max_length=500, validators=[
        url_validator], null=True)
    duration = models.DurationField(null=True)
    ###

    external_urls = models.URLField(max_length=500, validators=[
        url_validator], blank=True, null=True)
    source = models.CharField(max_length=50, null=True)  # KeyPoints or YouTube
    title = models.TextField(null=True)

    creator = models.ForeignKey(
        Creator, blank=False, null=True, on_delete=models.SET_NULL)
    categories = models.ManyToManyField(KeypointsCategoryTag, blank=True)
    languages = models.ManyToManyField(LanguageTag, blank=True)
    topics = models.ManyToManyField(KeypointsTopicTag, blank=True)
    hashtags = models.ManyToManyField(KeywordsTag, blank=True)

    views = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    shared = models.IntegerField(default=0)


class VideoBuffer(AbstractTimeClass):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    url = models.URLField(max_length=500, validators=[
                          url_validator], unique=True)
    title = models.TextField(null=True)
    thumbnail_image = models.URLField(max_length=500, validators=[
        url_validator], null=True)
    duration = models.DurationField(null=True)
    creator = models.ForeignKey(
        Creator, blank=False, null=True, on_delete=models.SET_NULL)
    categories = models.ManyToManyField(KeypointsCategoryTag, blank=True)
    languages = models.ManyToManyField(LanguageTag, blank=True)
    topics = models.ManyToManyField(KeypointsTopicTag, blank=True)
    hashtags = models.ManyToManyField(KeywordsTag, blank=True)

    checked = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)


class VideoReShare(AbstractTimeClass):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    video_id = models.ForeignKey(VideoPost, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class VideoLike(AbstractTimeClass):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    video_id = models.ForeignKey(VideoPost, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class meta:
        unique_together = ['video_id', 'user']


class AnnUserActivity(AbstractTimeClass):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ann_user = models.ForeignKey(
        AnnonymousUserTable, blank=True, on_delete=models.CASCADE)
    session = models.TextField(blank=True)
    page = models.TextField(blank=True)
    video_click = models.ForeignKey(
        VideoPost, blank=True, on_delete=models.CASCADE)
    length = models.DurationField()
    creator_click = models.ForeignKey(Creator, on_delete=models.CASCADE)
    hashtag_click = models.ForeignKey(KeywordsTag, on_delete=models.CASCADE)
