import os
import json
import hashlib

from constants import *

from media_ops.models import ImagesUrl, VideoUrl, AudioUrl

from popup_ops.models import ActionTag, PopupTag, Bbox
from popup_ops.models import KpMediaInfo
from popup_ops.models import OpenUrlData, DownloadData, SeekToData, PopupData
from popup_ops.models import PopupCarouselMapping, ActionDataMapping

from utils.video_utils import create_thumbnail_local_video, create_video_hash
from utils.video_utils import create_video_obj_from_file
from utils.text_utils import text_to_query
from utils.storage_utils import get_full_path

from popup_ops.utils.popup_utils import get_popup_instance_obj


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
        popup_instance_obj = get_popup_instance_obj(
            action_data.get('popup_obj', {}))
        action_obj = ActionDataMapping.objects.create(
            action_id=action_id, popup_id=popup_instance_obj)

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
