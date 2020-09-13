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
    video = models.ForeignKey(VideoUrl, on_delete=models.CASCADE)

    creator = models.ForeignKey(
        Creator, blank=False, null=True, on_delete=models.SET_NULL)
    title = models.TextField(null=True)
    external_urls = models.URLField(max_length=500, validators=[
        url_validator], blank=True, null=True)
    categories = models.ManyToManyField(KeypointsCategoryTag, blank=True)
    languages = models.ManyToManyField(LanguageTag, blank=True)
    topics = models.ManyToManyField(KeypointsTopicTag, blank=True)
    hashtags = models.ManyToManyField(KeywordsTag, blank=True)

    views = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    shared = models.IntegerField(default=0)

    @property
    def source(self):
        if self.video:
            return self.video.source
        return None

    @property
    def thumbnail_image(self):
        if self.video:
            return self.video.thumbnail_img
        return None

    @property
    def url(self):
        if self.video:
            if self.video.hls_url:
                return self.video.hls_url
            if self.video.compressed_url:
                return self.video.compressed_url
            return self.video.url
        return None


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
