import feedparser
from django.http import HttpRequest, QueryDict

from accounts.models import User, UserImagesUrl
from keypoints_account.models import Creator
from tags_models.models import LanguageTag, KeypointsCategoryTag

import pandas as pd
import random
import hashlib
import re

import string
import logging
logging.getLogger().setLevel(logging.INFO)

csv_file = "./z_data/user_seed_content.csv"
df = pd.read_csv(csv_file)

all_creator = Creator.objects.all().update(is_active=False)

Creator.objects.all().delete()

for row in df.itertuples():
    index = row.user_id
    user_name = row.user_name.strip()
    logo_url = row.logo_url
    categories = row.categories
    language = row.language
    channel_link = row.channel_link

    phone_number = int("1%09d" % (index))

    hash_val = hashlib.md5(logo_url.encode('utf-8')).hexdigest()
    profile_pic, _ = UserImagesUrl.objects.get_or_create(image_url=logo_url,
                                                         image_hash=hash_val)
    user_obj, _ = User.objects.update_or_create(phone=phone_number,
                                                defaults={
                                                    "first_name": user_name,
                                                    "profile_pic": profile_pic
                                                })
    creator_obj, _ = Creator.objects.update_or_create(
        channel_link=channel_link, defaults={'user': user_obj,
                                             'username': user_name.replace(' ', ''),
                                             'is_active': True})

    categories = [] if pd.isnull(categories) else categories.split(', ')
    for category in categories:
        key = re.sub("[^a-z]+", "", category.lower())
        category_obj = KeypointsCategoryTag.objects.filter(key=key).first()
        if category_obj:
            creator_obj.categories.add(category_obj)
        else:
            logging.info("Category not found :: %s" % category)

    language = [] if pd.isnull(language) else language.split(', ')
    for lang in language:
        key = re.sub("[^a-z]+", "", lang.lower())
        language_obj = LanguageTag.objects.filter(key=key).first()
        if language_obj:
            creator_obj.languages.add(language_obj)
        else:
            logging.info("language not found :: %s" % lang)

    creator_obj.save()
