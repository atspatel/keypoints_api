import os
import json
import hashlib

from constants import *

from media_ops.models import ImagesUrl, VideoUrl, AudioUrl

from popup_ops.models import ActionTag, PopupTag, Bbox
from popup_ops.models import KpMediaInfo, ButtonData, MediaButtonMapping
from popup_ops.models import OpenUrlData, DownloadData, SeekToData, PopupData
from popup_ops.models import PopupCarouselMapping, ActionDataMapping

from utils.video_utils import create_thumbnail_local_video, create_video_hash
from utils.video_utils import create_video_obj_from_file
from utils.text_utils import text_to_query


def validate_bbox(top, left, width, height):
    if top != None and left != None and width != None and height != None:
        return True
    return False


def create_bbox_obj(bbox):
    bbox_obj = None
    top = bbox.get('top', None)
    left = bbox.get('left', None)
    width = bbox.get('width', None)
    height = bbox.get('height', None)

    if validate_bbox(top, left, width, height):
        bbox_obj, _ = Bbox.objects.get_or_create(
            top=top, left=left, width=width, height=height)
    return bbox_obj


def create_action_object(action, action_data):
    action_obj = None
    action_id = ActionTag.objects.filter(key=text_to_query(action)).first()
    if action == "openPopup":
        popup_type = action_data.get('popup_type', None)
        bbox = action_data.get('bbox', None)
        bbox_obj = create_bbox_obj(bbox)

        pause_video = action_data.get('pause_video', True)
        show_overlay_button = action_data.get('show_overlay_button', False)
        show_close_button = action_data.get('show_close_button', True)
        in_duration = action_data.get('in_duration', 1.0)

        popup_type_obj = PopupTag.objects.filter(
            key=text_to_query(popup_type)).first()
        popup_obj = PopupData.objects.create(
            popup_type=popup_type_obj,
            bbox=bbox_obj,
            pause_video=pause_video,
            show_overlay_button=show_overlay_button,
            show_close_button=show_close_button,
            in_duration=in_duration
        )

        if popup_type == "mediaCarousel":
            media_list = action_data.get('media_list', [])

            for media in media_list:
                media_type = media.get('type', None)
                source = media.get('source', None)
                index = media.get('index', None)
                if media_type == "image":
                    image_hash = hashlib.md5(
                        source.encode('utf-8')).hexdigest()
                    image_obj, _ = ImagesUrl.objects.update_or_create(image_hash=image_hash, defaults={
                        "image_url": source,
                        "thumbnail_img": source,
                        "media_type": 'image/external'})
                    media_obj = KpMediaInfo.objects.create(
                        media_type=MEDIA_TYPE_IMAGE, image_url=image_obj)

                    PopupCarouselMapping.objects.update_or_create(
                        popup_id=popup_obj, media=media_obj, defaults={'index': index})

                # elif media_type == "video":

                # elif media_type == "audio":

        action_obj = ActionDataMapping.objects.create(
            action_id=action_id, popup_id=popup_obj)
    # elif action == "seekTo":
    #     duration = action_data.get('seekTo', None)
    #     toPlay = action_data.get('toPlay', None)

    # elif action == "download":
    #     url = action_data.get('url', None)
    #     filename = action_data.get('filename', None)

    # elif action == "openUrl":
    #     url = action_data.get('url', None)

    return action_obj
