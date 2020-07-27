import feedparser
from django.http import HttpRequest, QueryDict

from keypoints_account.models import Creator
from keypoints.models import VideoPost
from media_ops.models import VideoUrl
from tags_models.models import KeypointsCategoryTag, KeypointsTopicTag
from tags_models.models import LanguageTag, KeywordsTag

from utils.website_info import get_website_info
from utils.text_utils import text_to_query
from utils.video_utils import create_thumbnail_local_video, create_video_hash, create_video_obj_from_file

import pandas as pd
import random
import hashlib
import re

import string
import logging
logging.getLogger().setLevel(logging.INFO)

exclude_keys = ["highlites", "mondaymotivation", "thursdayvibes", "tuesdaythoughts",
                "thursdaymorning", "sundaythoughts", "tuesdaymotivation", "wednesdaywisdom"]

csv_file = "./z_data/video_seed_content.csv"
df = pd.read_csv(csv_file)

# finput = "./z_data/content_videos/UGU1BQsWIKXWF55X.mp4"
# create_thumbnail_local_video(finput)

for row in df.itertuples():
    video_filename = row.video_file_name
    filePath = os.path.join("./z_data/content_videos/", video_filename)
    title = row.video_title
    user_name = row.user_id.strip()
    categories = row.categories
    languages = row.languages
    topics = row.topics
    hashtags = row.hashtags
    ext_url = row.ext_url

    video_hash = create_video_hash(filePath)
    thumbnail_image = create_thumbnail_local_video(filePath)

    creator_obj = Creator.objects.filter(user__first_name=user_name).first()
    if not creator_obj:
        logging.info('Creator Not Found ::: ', user_name)
    video_obj = VideoUrl.objects.filter(video_hash=video_hash).first()
    if not video_obj:
        video_obj = create_video_obj_from_file(
            filePath, video_hash, thumbnail_image, user=creator_obj.user)
    post_obj, _ = VideoPost.objects.update_or_create(
        video=video_obj, defaults={
            "creator": creator_obj,
            "title": title,
            "external_urls": ext_url}
    )
    categories = [] if pd.isnull(categories) else categories.split(', ')
    for category in categories:
        if(category == "General"):
            category = "Explore"
        key = re.sub("[^a-z]+", "", category.lower())
        category_obj = KeypointsCategoryTag.objects.filter(key=key).first()
        if category_obj:
            post_obj.categories.add(category_obj)
        else:
            logging.info("Category not found :: ", category)

    languages = [] if pd.isnull(languages) else languages.split(', ')
    for language in languages:
        key = re.sub("[^a-z]+", "", language.lower())
        language_obj = LanguageTag.objects.filter(key=key).first()
        if language_obj:
            post_obj.languages.add(language_obj)
        else:
            logging.info("language not found :: ", language)

    topics = [] if pd.isnull(topics) else topics.split(', ')
    for topic in topics:
        key = text_to_query(topic)
        if not key:
            continue
        topic_obj, _ = KeypointsTopicTag.objects.get_or_create(
            key=key, defaults={'tag': topic})
        post_obj.topics.add(topic_obj)

    hashtags = [] if pd.isnull(hashtags) else hashtags.split('#')
    for hashtag in hashtags:
        hashtag = hashtag.strip()
        key = text_to_query(hashtag)
        if not key:
            continue
        if key in exclude_keys:
            continue
        keywords_obj, _ = KeywordsTag.objects.get_or_create(
            key=key, defaults={'tag': hashtag})
        post_obj.hashtags.add(keywords_obj)

    post_obj.save()
