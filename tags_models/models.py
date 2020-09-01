from django.core.validators import URLValidator
import uuid
from django.db import models

from django.conf import settings
User = settings.AUTH_USER_MODEL
# Create your models here.
url_validator = URLValidator(
    schemes=('http', 'https', 'ftp', 'ftps', 'rtsp', 'rtmp'))


class AbstractTimeClass(models.Model):
    created_by = models.ForeignKey(
        User, related_name='%(class)s_created_by', on_delete=models.SET_NULL, null=True, blank=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class LanguageTag(AbstractTimeClass):
    key = models.CharField(max_length=200, unique=True)
    tag = models.TextField()
    thumbnail_img = models.URLField(max_length=500, validators=[
        url_validator], null=True, blank=True)
    isAppLive = models.BooleanField(default=False)

    def __str__(self):
        return "%s--%s" % (self.id, self.tag)


class KeywordsTag(AbstractTimeClass):
    key = models.CharField(max_length=200, unique=True)
    tag = models.TextField()
    category = models.CharField(max_length=100, default='keywords')

    is_display = models.BooleanField(default=True)

    def __str__(self):
        return "%s--%s" % (self.id, self.tag)


class KeypointsCategoryTag(AbstractTimeClass):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    key = models.CharField(max_length=200, unique=True)
    tag = models.TextField()
    index = models.IntegerField(default=999)
    num_of_posts = models.IntegerField(default=0)
    thumbnail_img = models.URLField(max_length=500, validators=[
        url_validator], null=True, blank=True)

    def __str__(self):
        return "%s--%s" % (self.index, self.tag)


class KeypointsTopicTag(AbstractTimeClass):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    key = models.CharField(max_length=200, unique=True)
    tag = models.TextField()
    categories = models.ManyToManyField(KeypointsCategoryTag, blank=True)
    thumbnail_img = models.URLField(max_length=500, validators=[
        url_validator], null=True, blank=True)
    followers = models.IntegerField(default=0)
    num_of_posts = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return "%s--%s" % (self.id, self.tag)
