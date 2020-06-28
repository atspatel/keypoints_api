import feedparser
from django.http import HttpRequest, QueryDict

from keypoints_account.models import Creator
from keypoints.models import VideoPost
from tags_models.models import KeypointsCategoryTag, KeypointsTopicTag
from tags_models.models import LanguageTag, KeywordsTag

from utils.website_info import get_website_info
from utils.text_utils import text_to_query

import pandas as pd
import random
import hashlib
import re

import string

csv_file = "./z_data/video_seed_content.csv"
df = pd.read_csv(csv_file)

for row in df.itertuples():
    video_url = row.video_url
    video_title = row.video_title
    user_name = row.user_id.strip()
    categories = row.categories
    languages = row.languages
    topics = row.topics
    hashtags = row.hashtags

    video_info = get_website_info(video_url)
    title = video_info['title']
    duration = video_info['duration']
    media_thumbnail = video_info['image_url'][0] if(
        len(video_info['image_url']) > 0) else None

    creator_obj = Creator.objects.filter(user__first_name=user_name).first()
    if not creator_obj:
        print('Creator Not Found ::: ', user_name)
    videoPost_obj, _ = VideoPost.objects.update_or_create(
        url=video_url, defaults={'title': video_title,
                                 'thumbnail_image': media_thumbnail,
                                 #  "duration": duration,
                                 "creator": creator_obj,
                                 "source": "youtube"})

    categories = [] if pd.isnull(categories) else categories.split(', ')
    for category in categories:
        if(category == "General"):
            category = "Explore"
        key = re.sub("[^a-z]+", "", category.lower())
        category_obj = KeypointsCategoryTag.objects.filter(key=key).first()
        if category_obj:
            videoPost_obj.categories.add(category_obj)
        else:
            print("Category not found :: ", category)

    languages = [] if pd.isnull(languages) else languages.split(', ')
    for language in languages:
        key = re.sub("[^a-z]+", "", language.lower())
        language_obj = LanguageTag.objects.filter(key=key).first()
        if language_obj:
            videoPost_obj.languages.add(language_obj)
        else:
            print("language not found :: ", language)

    topics = [] if pd.isnull(topics) else topics.split(', ')
    for topic in topics:
        key = text_to_query(topic)
        if not key:
            continue
        topic_obj, _ = KeypointsTopicTag.objects.get_or_create(
            key=key, defaults={'tag': topic})
        videoPost_obj.topics.add(topic_obj)

    hashtags = [] if pd.isnull(hashtags) else hashtags.split('#')
    for hashtag in hashtags:
        hashtag = hashtag.strip()
        key = text_to_query(hashtag)
        if not key:
            continue
        keywords_obj, _ = KeywordsTag.objects.get_or_create(
            key=key, defaults={'tag': hashtag})
        videoPost_obj.hashtags.add(keywords_obj)

    videoPost_obj.save()
