from rest_framework.views import APIView
from rest_framework.response import Response

from .models import LanguageTag, KeywordsTag
from .models import KeypointsTopicTag, KeypointsCategoryTag
from .serializers import LanguageTagSerializer

from utils.text_utils import text_to_query


def add_languages(languages, post_obj, buffer_obj=None):
    if buffer_obj:
        buffer_obj.languages.clear()
    post_obj.languages.clear()

    for tag in languages:
        key = text_to_query(tag)
        if key:
            obj = LanguageTag.objects.filter(key=key).first()
            if obj:
                post_obj.languages.add(obj)
                if buffer_obj:
                    buffer_obj.languages.add(obj)
    return post_obj, buffer_obj


def add_categories(categories, post_obj, buffer_obj=None):
    if buffer_obj:
        buffer_obj.categories.clear()
    post_obj.categories.clear()

    for tag in categories:
        key = text_to_query(tag)
        if key:
            obj = KeypointsCategoryTag.objects.filter(key=key).first()
            if obj:
                post_obj.categories.add(obj)
                if buffer_obj:
                    buffer_obj.categories.add(obj)
    return post_obj, buffer_obj


def add_topics(topics, post_obj, buffer_obj=None):
    if buffer_obj:
        buffer_obj.topics.clear()
    post_obj.topics.clear()
    for tag in topics:
        key = text_to_query(tag)
        if key:
            obj, _ = KeypointsTopicTag.objects.get_or_create(
                key=key, defaults={"tag": tag})
            post_obj.topics.add(obj)
            if buffer_obj:
                buffer_obj.topics.add(obj)
    return post_obj, buffer_obj


def add_hashtags(hashtags, post_obj, buffer_obj=None):
    if buffer_obj:
        buffer_obj.hashtags.clear()
    post_obj.hashtags.clear()

    for tag in hashtags:
        key = text_to_query(tag)
        if key:
            obj, _ = KeywordsTag.objects.get_or_create(
                key=key, defaults={"tag": tag})
            post_obj.hashtags.add(obj)
            if buffer_obj:
                buffer_obj.hashtags.add(obj)
    return post_obj, buffer_obj


class LanguageView(APIView):
    def get(self, request, suggestion_text=None):
        if(suggestion_text):
            queryset = LanguageTag.objects.filter(tag__iregex=r"{0}".format(suggestion_text)
                                                  ).order_by('-creation_date')

        else:
            queryset = LanguageTag.objects.all().order_by('-creation_date')
        language_tag = LanguageTagSerializer(queryset, many=True).data
        return Response({"data": language_tag, "status": True})

    def post(self, request):
        pass
