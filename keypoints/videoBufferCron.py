import feedparser
from django.http import HttpRequest, QueryDict

from keypoints.models import Creator, VideoBuffer, VideoPost
from tags_models.models import KeywordsTag
from utils.website_info import get_website_info
from utils.date_parser import get_date_from_str
from utils.text_utils import text_to_query

import datetime
import pytz
import re
import json
import isodate

import ssl
import logging
logging.getLogger().setLevel(logging.INFO)

if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context


VideoBuffer.objects.all().delete()
all_creator_account = Creator.objects.filter(is_active=True)

for p_account in all_creator_account:
    if p_account.rss_feed == None:
        continue

    feed_url = p_account.rss_feed
    categories = p_account.categories
    languages = p_account.languages

    last_croned = p_account.last_croned

    crr_time = datetime.datetime.now(pytz.timezone('Asia/Kolkata'))
    if last_croned and (crr_time - last_croned) < datetime.timedelta(minutes=10):
        # will wait for 10 min before next cron
        logging.info("---- skipping ... ", p_account.rss_feed)
        continue

    logging.info("++++ croning ... ", feed_url)
    videoFeed = feedparser.parse(feed_url)

    prev_skipped_link = 0
    for entry in videoFeed.entries:
        # try:
        if prev_skipped_link >= 3:
            break

        link = entry['link'].strip()
        date_str = entry.get('published', None)  # 2020-05-26T07:38:55+00:00
        if VideoBuffer.objects.filter(url=link).first():
            logging.info("already created videoBuffer with url :: ", link)
            prev_skipped_link += 1
            continue

        if VideoPost.objects.filter(url=link).first():
            logging.info("already created videoPost with url :: ", link)
            prev_skipped_link += 1
            continue

        # get_date from youtube

        days_span = 300
        date_published = get_date_from_str(date_str)
        crr_time = datetime.datetime.now(pytz.timezone('Asia/Kolkata'))
        if (crr_time - date_published) > datetime.timedelta(days=days_span):
            logging.info("skipping .... , Posted before range : %d days" %
                         (days_span))
            continue
        video_info = get_website_info(link)
        title = video_info['title']
        description = video_info['description']
        duration = video_info['duration']
        if duration:
            duration = isodate.parse_duration(duration).total_seconds()
            duration = datetime.timedelta(seconds=duration)
        media_thumbnail = video_info['image_url'][0] if(
            len(video_info['image_url']) > 0) else None

        VideoBuffer_obj = VideoBuffer.objects.create(
            url=link, title=title,
            duration=duration,
            creator=p_account,
            thumbnail_image=media_thumbnail,
            creation_date=date_published)

        for category in p_account.categories.all():
            VideoBuffer_obj.categories.add(category)
        for language in p_account.languages.all():
            VideoBuffer_obj.languages.add(language)

        # add hashtags....
        hashtags = video_info.get('keywords', [])
        if hashtags:
            for hashtag_str in hashtags:
                for hashtag in hashtag_str.split(','):
                    hashtag = hashtag.strip()
                    key = text_to_query(hashtag)
                    if not key:
                        continue
                    keywords_obj, _ = KeywordsTag.objects.get_or_create(
                        key=key, defaults={'tag': hashtag})
                    VideoBuffer_obj.hashtags.add(keywords_obj)

        VideoBuffer_obj.save()

    # p_account.last_croned = crr_time
    # p_account.save()
