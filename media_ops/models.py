from django.db import models
from django.utils import timezone
from django.core.validators import URLValidator
import uuid

from accounts.models import User

url_validator = URLValidator(
    schemes=('http', 'https', 'ftp', 'ftps', 'rtsp', 'rtmp'))


class AbstractTimeClass(models.Model):
    created_by = models.ForeignKey(
        User, related_name='%(class)s_created_by', on_delete=models.SET_NULL, null=True)
    creation_date = models.DateTimeField(default=timezone.now, blank=True)
    creation_date.editable = True
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class ImagesUrl(AbstractTimeClass):
    image_url = models.URLField(max_length=300, validators=[url_validator])
    image_hash = models.CharField(max_length=300, unique=True)
    thumbnail_img = models.URLField(max_length=300, validators=[
                                    url_validator], null=True, blank=True)
    media_type = models.CharField(max_length=100, default='image/jpeg')

    @property
    def display_url(self):
        return self.image_url


class VideoUrl(AbstractTimeClass):
    video_hash = models.CharField(max_length=300, unique=True)
    url = models.URLField(max_length=300, validators=[
        url_validator], unique=True)
    thumbnail_img = models.URLField(max_length=300, validators=[
        url_validator], null=True, blank=True)

    hls_url = models.URLField(max_length=500, validators=[
        url_validator], blank=True, null=True)
    compressed_url = models.URLField(max_length=500, validators=[
        url_validator], blank=True, null=True)

    duration = models.DurationField(null=True)
    media_type = models.CharField(max_length=100, default='video/mp4')
    source = models.CharField(max_length=50, default="KeyPoints")

    @property
    def display_url(self):
        if self.hls_url:
            return self.hls_url
        else:
            return self.url


class AudioUrl(AbstractTimeClass):
    audio_hash = models.CharField(max_length=300, unique=True)
    url = models.URLField(max_length=300, validators=[
        url_validator], unique=True)
    thumbnail_img = models.URLField(max_length=300, validators=[
        url_validator], null=True, blank=True)

    duration = models.DurationField(null=True)
    media_type = models.CharField(max_length=100, default='audio/mpeg')
    source = models.CharField(max_length=50, default="KeyPoints")

    @property
    def display_url(self):
        return self.url
