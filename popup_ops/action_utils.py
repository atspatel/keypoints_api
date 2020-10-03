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
from utils.storage_utils import get_full_path


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
        popup_info = action_data.get('popup_info', None)
        if popup_info:
            popup_type = popup_info.get('popupType', None)
            bbox = popup_info.get('bbox', None)
            pause_video = popup_info.get('pauseVideo', True)
            show_overlay_button = popup_info.get('showOverlayButton', False)
            show_close_button = popup_info.get('showCloseButton', True)
            in_duration = popup_info.get('inDuration', 1.0)

            popup_type_obj = PopupTag.objects.filter(
                key=text_to_query(popup_type)).first()
            bbox_obj = create_bbox_obj(bbox)
            popup_obj = PopupData.objects.create(
                popup_type=popup_type_obj,
                bbox=bbox_obj,
                pause_video=pause_video,
                show_overlay_button=show_overlay_button,
                show_close_button=show_close_button,
                in_duration=in_duration
            )

            if popup_type == "mediaCarousel":
                media_list = action_data.get('data', [])

                for media in media_list:
                    media_type = media.get('type', None)
                    source = media.get('source', None)
                    if source:
                        source = get_full_path(source)
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

    elif action == "seekTo":
        duration = action_data.get('duration', None)
        toPlay = action_data.get('toPlay', False)

        seekTo_obj, _ = SeekToData.objects.get_or_create(
            duration=duration, toPlay=toPlay)
        action_obj = ActionDataMapping.objects.create(
            action_id=action_id, seekto_id=seekTo_obj)

    elif action == "download":
        url = action_data.get('url', None)
        filename = action_data.get('filename', None)

        download_obj, _ = DownloadData.objects.get_or_create(
            url=url, filename=filename)
        action_obj = ActionDataMapping.objects.create(
            action_id=action_id, download_id=download_obj)

    elif action == "openUrl":
        url = action_data.get('url', None)
        inPopup = action_data.get('inPopup', False)

        openurl_obj, _ = OpenUrlData.objects.get_or_create(
            url=url, inPopup=inPopup)
        action_obj = ActionDataMapping.objects.create(
            action_id=action_id, openurl_id=openurl_obj)

    return action_obj


def create_button_obj(button):
    action = button.get('action', None)
    action_type = action.get('type', None)
    action_data = action.get('data', None)
    action_obj = create_action_object(action_type, action_data)

    bbox = button.get('bbox', None)
    bbox_obj = create_bbox_obj(bbox)

    button_obj = ButtonData.objects.create(
        name=button.get('name', None),
        start=button.get('start', None),
        end=button.get('end', None),
        bbox=bbox_obj,
        shape=button.get('shape', None),
        pause_video_dur=button.get('pauseVideo', None),
        background_img=button.get('background_img', None),
        action_id=action_obj
    )

    return button_obj


def create_media_object(media_info, video_obj):

    # TODO :: Create video obj and add audio and image object
    media_obj = None
    media_id = media_info.get("id", None)
    if media_id:
        media_obj = KpMediaInfo.objects.filter(id=media_id).first()
        print("------", media_obj.id)

    if not media_obj:
        name = media_info.get('name', None)
        media_obj, _ = KpMediaInfo.objects.update_or_create(
            video_url=video_obj, defaults={"media_type": MEDIA_TYPE_VIDEO, "name": name})

        MediaButtonMapping.objects.filter(media=media_obj).delete()
        butttons = media_info.get('buttons', [])
        for button in butttons:
            button_obj = create_button_obj(button)
            MediaButtonMapping.objects.get_or_create(
                media=media_obj, button=button_obj)

    return media_obj
