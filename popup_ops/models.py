from django.db import models
from django.utils import timezone
from django.core.validators import URLValidator
import uuid

from accounts.models import User
from media_ops.models import AudioUrl, VideoUrl, ImagesUrl
from tags_models.models import LanguageTag

from constants import *
url_validator = URLValidator(
    schemes=('http', 'https', 'ftp', 'ftps', 'rtsp', 'rtmp'))

action = ['changeVideo', 'changeAudio',
          'openUrl', 'download', 'seekTo', 'openPopup']

popup = ['mediaCarousel', 'html']

shape = [[SHAPE_RECT, SHAPE_RECT],
         [SHAPE_SQUARE, SHAPE_SQUARE],
         [SHAPE_CIRCLE, SHAPE_CIRCLE]]

media_types = [[MEDIA_TYPE_IMAGE, MEDIA_TYPE_IMAGE],
               [MEDIA_TYPE_AUDIO, MEDIA_TYPE_AUDIO],
               [MEDIA_TYPE_VIDEO, MEDIA_TYPE_VIDEO],
               [MEDIA_TYPE_PLAYLIST, MEDIA_TYPE_PLAYLIST]]


class AbstractTimeClass(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_by = models.ForeignKey(
        User, related_name='%(class)s_created_by', on_delete=models.SET_NULL, null=True)
    creation_date = models.DateTimeField(default=timezone.now, blank=True)
    creation_date.editable = True
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class ActionTag(AbstractTimeClass):
    key = models.CharField(max_length=200, unique=True)
    tag = models.TextField()

    def __str__(self):
        return self.tag


class PopupTag(AbstractTimeClass):
    key = models.CharField(max_length=200, unique=True)
    tag = models.TextField()

    def __str__(self):
        return self.tag


class Bbox(AbstractTimeClass):
    top = models.FloatField()
    left = models.FloatField()
    width = models.FloatField()
    height = models.FloatField()


class KpMediaInfo(AbstractTimeClass):
    media_type = models.CharField(max_length=50, choices=media_types)
    name = models.TextField(null=True, blank=True)

    video_url = models.ForeignKey(
        VideoUrl, blank=True, null=True, on_delete=models.CASCADE)
    audio_url = models.ForeignKey(
        AudioUrl, blank=True, null=True, on_delete=models.CASCADE)
    image_url = models.ForeignKey(
        ImagesUrl, blank=True, null=True, on_delete=models.CASCADE)

    # title = models.ForeignKey(
    #     Title, blank=True, null=True, on_delete=models.SET_NULL)
    language = models.ForeignKey(
        LanguageTag, blank=True, null=True, on_delete=models.SET_NULL)


class OpenUrlData(AbstractTimeClass):
    url = models.URLField(max_length=300, validators=[url_validator])
    inPopup = models.BooleanField(default=False)


class DownloadData(AbstractTimeClass):
    url = models.URLField(max_length=300, validators=[url_validator])
    filename = models.TextField()


class SeekToData(AbstractTimeClass):
    duration = models.FloatField(default=0.0)
    toPlay = models.BooleanField(False)


class PopupData(AbstractTimeClass):
    popup_type = models.ForeignKey(
        PopupTag, null=True, on_delete=models.SET_NULL)
    bbox = models.ForeignKey(Bbox, null=True, on_delete=models.SET_NULL)
    pause_video = models.BooleanField(default=True)
    show_overlay_button = models.BooleanField(default=False)
    show_close_button = models.BooleanField(default=True)
    in_duration = models.FloatField(default=1.0)


class PopupCarouselMapping(AbstractTimeClass):
    popup_id = models.ForeignKey(
        PopupData, null=True, on_delete=models.SET_NULL)
    media = models.ForeignKey(KpMediaInfo, null=True,
                              on_delete=models.SET_NULL)
    index = models.IntegerField(default=999)


class ActionDataMapping(AbstractTimeClass):
    action_id = models.ForeignKey(
        ActionTag, null=True, on_delete=models.SET_NULL)

    openurl_id = models.ForeignKey(
        OpenUrlData, null=True, on_delete=models.CASCADE)
    download_id = models.ForeignKey(
        DownloadData, null=True, on_delete=models.CASCADE)
    seekto_id = models.ForeignKey(
        SeekToData, null=True, on_delete=models.CASCADE)
    popup_id = models.ForeignKey(
        PopupData, null=True, on_delete=models.CASCADE)


class ButtonData(AbstractTimeClass):
    name = models.TextField(null=True)
    start = models.FloatField(default=0.0)
    end = models.FloatField(default=-1)
    bbox = models.ForeignKey(Bbox, null=True, on_delete=models.SET_NULL)
    shape = models.CharField(max_length=20, blank=True, null=True)
    background_img = models.URLField(
        max_length=300, null=True, validators=[url_validator])
    action_id = models.ForeignKey(ActionDataMapping, on_delete=models.CASCADE)


class MediaButtonMapping(AbstractTimeClass):
    media = models.ForeignKey(KpMediaInfo, on_delete=models.CASCADE)
    button = models.ForeignKey(ButtonData, on_delete=models.CASCADE)
    index = models.IntegerField(default=-1)
