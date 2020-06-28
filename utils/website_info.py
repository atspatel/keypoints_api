import constants

import tweepy
import json
import requests
from bs4 import BeautifulSoup
from link_preview import link_preview


url_meta_mapping = {
    'title': ['title', 'og:title', 'twitter:title'],
    'description': ['description', 'og:description', 'twitter:description'],
    'image_url': ['og:image', 'image'],
    'site_name': ['og:site_name', 'website'],
    'android_url': ['al:android:url'],
    'ios_url': ['al:ios:url'],
    'content_type': ['og:type'],
    'video_url': ['og:video:url'],
    'video_tag': ['og:video:tag'],
    'keywords': ['keywords'],
    'duration': ['duration'],
    'isFamilyFriendly': ['isFamilyFriendly'],
    'datePublished':  ['datePublished'],
    'genre': ['genre']
}
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

# ACCESS_TOKEN = constants.ACCESS_TOKEN
# ACCESS_SECRET = constants.ACCESS_SECRET
# CONSUMER_KEY = constants.CONSUMER_KEY
# CONSUMER_SECRET = constants.CONSUMER_SECRET


class TwitterStatus():
    def __init__(self):
        auth = tweepy.OAuthHandler(
            constants.CONSUMER_KEY, constants.CONSUMER_SECRET)
        auth.set_access_token(constants.ACCESS_TOKEN, constants.ACCESS_SECRET)
        self.api = tweepy.API(auth, wait_on_rate_limit=True,
                              wait_on_rate_limit_notify=True, compression=False)

    def get_tweet_status_info(self, twitter_url):
        base_url = twitter_url.split("?")[0]
        status_code = base_url.split("/")[-1]
        image_url = []
        video_url = []
        duration = None
        try:
            r = self.api.get_status(status_code, tweet_mode='extended')
            result = r._json

            full_text = result['full_text']
            extended_entities = result.get('extended_entities', {})
            for media in extended_entities.get('media', []):
                if media['type'] == "photo":
                    image_url.append(media['media_url_https'])
                    full_text = full_text.replace(media['url'], '')
                elif media['type'] == 'video':
                    thumbnail = media['media_url_https']
                    duration = media['video_info']['duration_millis']
                    video_url_variants = media['video_info']['variants']
                    for variant in video_url_variants:
                        if (variant['content_type'] == "application/x-mpegURL"):
                            video_url.append(
                                {"url": variant['url'], "thumbnail": thumbnail})
                    full_text = full_text.replace(media['url'], '')

            output = {
                "title": result['user']['name'],
                "description": full_text,
                "site_name": "Twitter",
                "content_type": 'tweet',
                "duration": duration,
                "isFamilyFriendly": result.get('possibly_sensitive', True),
                "datePublished": result['created_at'],
                'genre': None,

                "image_url": image_url,
                "video_url": video_url,
                "keywords": [hashtag["text"] for hashtag in result['entities']['hashtags']]
            }
            return output
        except:
            return None


def meta_data_to_url_info(meta_info_dict):
    url_info = {
        'title': None,
        'description': None,
        'site_name': None,
        'android_url': None,
        'ios_url': None,
        'content_type': None,
        'duration': None,
        'isFamilyFriendly': True,
        'datePublished': None,
        'genre': None,

        'image_url': [],
        'video_url': [],
        'video_tag': [],
        'keywords': []
    }
    for k in url_info:
        for meta_tag in url_meta_mapping[k]:
            value = meta_info_dict.get(meta_tag, None)
            if value:
                if isinstance(url_info[k], list):
                    url_info[k] = value
                else:
                    url_info[k] = value[0]
                break
    url_info['video_url'] = [{'url': url, 'thumbnail': None}
                             for url in url_info['video_url']]
    return url_info


def get_website_info(url):
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content.decode('utf-8'))

    meta_info_dict = {}
    metas = soup.find_all('meta')
    for meta in metas:
        value = meta.get('content', None)
        if not value:
            continue
        for k in ['name', 'property', 'itemprop']:
            key = meta.get(k, None)
            if key:
                if key not in meta_info_dict:
                    meta_info_dict[key] = []
                meta_info_dict[key].append(value)

    return meta_data_to_url_info(meta_info_dict)


def meta_data_from_url(url, twitter_class=None):
    try:
        if url.startswith("https://twitter.com/"):
            if twitter_class:
                res = twitter_class.get_tweet_status_info(url)
                return res
            meta_info_dict = link_preview.generate_dict(url)
            meta_info_dict = {k: [v] for k, v in meta_info_dict.items()}
            return meta_data_to_url_info(meta_info_dict)

        return get_website_info(url)
    except:
        return None
