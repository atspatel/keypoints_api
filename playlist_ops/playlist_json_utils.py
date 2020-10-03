import constants
from popup_ops.models import KpMediaInfo
from playlist_ops.models import Title, Button
from tags_models.models import LanguageTag

from utils.text_utils import text_to_query
from utils.storage_utils import get_full_path

from constants import *
from media_ops.models import VideoUrl, AudioUrl

from popup_ops.action_utils import create_media_object

import hashlib
video_source = "KeyPoints"

storage_dir = constants.storage_dir


def get_title_obj(title, created_by=None):
    title_obj = None
    parent_title_obj = None

    for lang in ['hindi', 'english']:
        title_l = title.get(lang, None)
        if title_l:
            parent_lang = lang
            title_lang = LanguageTag.objects.filter(key=lang).first()
            parent_title_obj, _ = Title.objects.update_or_create(
                title_text=title_l, defaults={"language": title_lang, "created_by": created_by})
            break

    title_obj = parent_title_obj
    for lang, title_l in title.items():
        if lang == parent_lang:
            continue
        title_lang = LanguageTag.objects.filter(key=lang).first()
        title_obj, _ = Title.objects.update_or_create(
            title_text=title_l, defaults={
                "language": title_lang, "base_title": parent_title_obj, "created_by": created_by})
    return title_obj


def get_lang_obj(language):
    key = text_to_query(language) if language else None
    lang_obj = None
    if key:
        lang_obj = LanguageTag.objects.filter(key=key).first()
    return lang_obj


def get_button_obj(button_info):
    button_obj = None
    name = button_info.get("name", None)
    action = button_info.get("action", None)
    if name:
        button_obj, _ = Button.objects.update_or_create(
            name=name, action=action)
    return button_obj


def get_media_obj(media_info, storage_dir=storage_dir, created_by=None):
    media_obj = None
    media_id = media_info.get("id", None)
    if media_id:
        media_obj = KpMediaInfo.objects.filter(id=media_id).first()
        return media_obj

    media_data = media_info.get('media', {})
    src = media_data.get('src', None)
    if src:
        src = get_full_path(src)

        thumbnail = media_data.get('thumbnail', None)
        name = media_info.get('name', None)
        media_hash = hashlib.sha256(src.encode('utf-8')).hexdigest()

        if media_info.get('media_type', None) == "video":
            video_obj, _ = VideoUrl.objects.update_or_create(video_hash=media_hash, defaults={
                "url": src,
                "thumbnail_img": get_full_path(thumbnail),
                "hls_url": src,
                "media_type": "video/mp4",
                "source": video_source})
            media_obj = create_media_object(media_info, video_obj)
            # media_obj, _ = KpMediaInfo.objects.update_or_create(video_url=video_obj,
            #                                                     defaults={"media_type": MEDIA_TYPE_VIDEO})
        elif media_info.get('media_type', None) == "audio":
            audio_obj, _ = AudioUrl.objects.update_or_create(audio_hash=media_hash, defaults={
                "url": src,
                "thumbnail_img": thumbnail,
                "media_type": "audio/mpeg",
                "source": video_source})

            # TODO:: replace with create_media_object, add audio and images to create_media_object
            media_obj, _ = KpMediaInfo.objects.update_or_create(audio_url=audio_obj,
                                                                defaults={"media_type": MEDIA_TYPE_AUDIO})

        if media_obj:
            media_lang_obj = get_lang_obj(media_info.get('language', None))
            media_obj.language = media_lang_obj
            media_obj.save()
    return media_obj
