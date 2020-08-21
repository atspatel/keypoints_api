import feedparser
from django.http import HttpRequest, QueryDict

from accounts.models import User
from keypoints_account.models import Creator
from keypoints.models import VideoPost
from media_ops.models import VideoUrl, ImagesUrl
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

# video_file_name,video_title,user_id,
# categories, languages,topics,hashtags,ext_url,
# video_hash, url,hls_url,compressed_url,
# image_url,image_hash,thumbnail_img

exclude_keys = ["highlites", "mondaymotivation", "thursdayvibes", "tuesdaythoughts",
                "thursdaymorning", "sundaythoughts", "tuesdaymotivation", "wednesdaywisdom"]

csv_file = "./z_data/video_seed_content.csv"
df = pd.read_csv(csv_file)

default_user = User.objects.filter(phone='8953457318').first()

for row in df.itertuples():
    title = row.video_title
    user_name = row.user_id.strip()
    categories = row.categories
    languages = row.languages
    topics = row.topics
    hashtags = row.hashtags
    ext_url = row.ext_url

    creator_obj = Creator.objects.filter(user__first_name=user_name).first()
    if not creator_obj:
        logging.info('Creator Not Found ::: %s' % user_name)

    image_url = row.image_url
    image_hash = row.image_hash
    thumbnail_img = row.thumbnail_img
    image_obj, _ = ImagesUrl.objects.update_or_create(image_hash=image_hash, defaults={
        "image_url": image_url,
        "thumbnail_img": thumbnail_img,
        "media_type": 'image/external',
        "created_by": default_user})

    video_hash = row.video_hash
    url = row.url
    hls_url = row.hls_url
    compressed_url = row.compressed_url
    thumbnail_img = image_obj.thumbnail_img

    video_obj, _ = VideoUrl.objects.update_or_create(video_hash=video_hash, defaults={
        "url": url,
        "thumbnail_img": thumbnail_img,
        "hls_url": hls_url,
        "compressed_url": compressed_url
    })

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
            logging.info("Category not found :: %s" % category)

    languages = [] if pd.isnull(languages) else languages.split(', ')
    for language in languages:
        key = re.sub("[^a-z]+", "", language.lower())
        language_obj = LanguageTag.objects.filter(key=key).first()
        if language_obj:
            post_obj.languages.add(language_obj)
        else:
            logging.info("language not found :: %s" % language)

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
