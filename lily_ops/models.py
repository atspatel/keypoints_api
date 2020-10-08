from django.db import models
from django.utils import timezone
from django.core.validators import URLValidator
import uuid

url_validator = URLValidator(
    schemes=('http', 'https', 'ftp', 'ftps', 'rtsp', 'rtmp'))


class AbstractTimeClass(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    creation_date = models.DateTimeField(default=timezone.now, blank=True)
    creation_date.editable = True
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class LilyCharacters(AbstractTimeClass):
    order = models.IntegerField(default=10)
    name = models.CharField(max_length=255, unique=True)
    thumbnail = models.URLField(max_length=500, validators=[
        url_validator], null=True, blank=True)
    color = models.CharField(max_length=10, null=True, blank=True)

    def __str__(self):
        if (self.name):
            return self.name
        return None


class Episode(AbstractTimeClass):
    ep = models.IntegerField()
    video_url = models.URLField(max_length=500, validators=[
        url_validator], null=True, blank=True)
    thumbnail = models.URLField(max_length=500, validators=[
        url_validator], null=True, blank=True)


class QuizInfo(AbstractTimeClass):
    name = models.CharField(max_length=255)
    quiz_type = models.CharField(max_length=255)
    ep = models.ForeignKey(Episode, null=True, on_delete=models.SET_NULL)
    start_time = models.IntegerField()
    end_time = models.IntegerField()
    question_part1 = models.TextField()
    question_part2 = models.TextField()
    isTimer = models.BooleanField(default=True)
    credit_video = models.URLField(max_length=500, validators=[
        url_validator], null=True, blank=True)

    def __str__(self):
        if (self.name):
            return self.name
        return None


class QuizActivity(AbstractTimeClass):
    session = models.UUIDField(default=uuid.uuid4, editable=False)
    quiz = models.ForeignKey(QuizInfo, null=True, on_delete=models.SET_NULL)
    answer = models.ForeignKey(
        LilyCharacters, null=True, on_delete=models.SET_NULL)


class QuizCharacterVoteCount(AbstractTimeClass):
    quiz = models.ForeignKey(QuizInfo, null=True, on_delete=models.SET_NULL)
    character = models.ForeignKey(
        LilyCharacters, null=True, on_delete=models.SET_NULL)
    number = models.IntegerField(default=1)
