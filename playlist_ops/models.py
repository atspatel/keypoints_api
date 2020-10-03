from django.db import models
from django.utils import timezone
from django.core.validators import URLValidator
import uuid

from accounts.models import User
from media_ops.models import AudioUrl, VideoUrl
from tags_models.models import LanguageTag

from popup_ops.models import KpMediaInfo

from constants import *
url_validator = URLValidator(
    schemes=('http', 'https', 'ftp', 'ftps', 'rtsp', 'rtmp'))

### action = ['changeVideo', 'changeAudio', 'openUrl', 'openPopup', 'download']

media_types = [[MEDIA_TYPE_VIDEO, MEDIA_TYPE_VIDEO],
               [MEDIA_TYPE_AUDIO, MEDIA_TYPE_AUDIO]]

media_categories = [[PRIMARY, PRIMARY], [SECONDARY, SECONDARY]]


class AbstractTimeClass(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_by = models.ForeignKey(
        User, related_name='%(class)s_created_by', on_delete=models.SET_NULL, null=True)
    creation_date = models.DateTimeField(default=timezone.now, blank=True)
    creation_date.editable = True
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Title(AbstractTimeClass):
    title_text = models.CharField(max_length=255)
    language = models.ForeignKey(
        LanguageTag, blank=True, null=True, on_delete=models.SET_NULL)
    base_title = models.ForeignKey(
        'self', blank=True, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        if (self.title_text):
            return self.title_text
        return None


class Button(AbstractTimeClass):
    name = models.CharField(max_length=255)
    action = models.CharField(
        max_length=255, blank=True, null=True)  # create tag models

    def __str__(self):
        if (self.name):
            return self.name
        return None


class PlaylistInfo(AbstractTimeClass):
    name = models.CharField(max_length=255)
    language = models.ForeignKey(
        LanguageTag, blank=False, null=True, on_delete=models.SET_NULL)
    title = models.ForeignKey(
        Title, blank=True, null=True, on_delete=models.SET_NULL)
    primary = models.CharField(max_length=50, choices=media_types)
    secondary = models.CharField(
        max_length=50, choices=media_types, blank=True, null=True)
    isSingleSecondary = models.BooleanField(default=True)


class PlaylistMediaMapping(AbstractTimeClass):
    playlist = models.ForeignKey(PlaylistInfo, on_delete=models.CASCADE)
    kp_media = models.ForeignKey(
        KpMediaInfo, null=True, on_delete=models.CASCADE)
    media_category = models.CharField(
        max_length=50, choices=media_categories)
    button = models.ForeignKey(
        Button, blank=True, null=True, on_delete=models.SET_NULL)
    title = models.ForeignKey(
        Title, blank=True, null=True, on_delete=models.SET_NULL)
    index = models.IntegerField(default=-1)
