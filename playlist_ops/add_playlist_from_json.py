import os
import json
import hashlib

from accounts.models import User

from playlist_ops.playlist_const import *
from playlist_ops.playlist_json_utils import get_title_obj, get_lang_obj, get_button_obj, get_media_obj

from playlist_ops.models import PlaylistInfo, PlaylistMediaMapping

admin_user = User.objects.filter(phone='8953457318').first()


json_folder = "./z_data/json_folder/"
for f in sorted(os.listdir(json_folder)):
    if not f.endswith(".json"):
        continue
    json_file_path = os.path.join(json_folder, f)

    data = json.load(open(json_file_path, 'r'))

    video_source = "ShareChat"

    parent_title_obj = None
    parent_lang = None

    title_obj = get_title_obj(data.get('title', {}), created_by=admin_user)
    lang_obj = get_lang_obj(data.get('language', "Hindi"))

    videoId = data.get('videoId', None)
    if videoId:
        primary = data.get('primary', 'video')
        primaryList = data.get('primaryList', [])

        secondary = data.get('secondary', None)

        isSingleSecondary = False
        secondaryList = []
        if secondary:
            isSingleSecondary = data.get('isSingleSecondary', False)
            secondaryList = data.get('secondaryList', [])
            if isSingleSecondary and len(secondaryList) > 1:
                secondaryList = secondaryList[:1]

        playlist_obj, _ = PlaylistInfo.objects.update_or_create(name=videoId, defaults={
            "language": lang_obj,
            "title": title_obj,
            "primary": primary.lower(),
            "secondary": secondary.lower() if secondary else None,
            "isSingleSecondary": isSingleSecondary,
            "created_by": admin_user
        })
        PlaylistMediaMapping.objects.filter(playlist=playlist_obj).delete()
        for index, media in enumerate(primaryList):
            media_obj = get_media_obj(media, created_by=admin_user)
            if media_obj:
                mapping_obj = PlaylistMediaMapping.objects.update_or_create(
                    playlist=playlist_obj, media=media_obj, defaults={'media_category': PRIMARY, "index": index})

        if secondary:
            for index, media in enumerate(secondaryList):
                media_obj = get_media_obj(media, created_by=admin_user)
                if media_obj:
                    mapping_obj = PlaylistMediaMapping.objects.update_or_create(
                        playlist=playlist_obj, media=media_obj, defaults={'media_category': SECONDARY, "index": index})

        print(f, playlist_obj.id)
