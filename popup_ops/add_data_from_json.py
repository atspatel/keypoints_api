import os
import json

from constants import *

from media_ops.models import ImagesUrl, VideoUrl, AudioUrl

from popup_ops.models import ActionTag, PopupTag, Bbox
from popup_ops.models import KpMediaInfo, ButtonData, MediaButtonMapping
from popup_ops.action_utils import create_action_object, create_bbox_obj

from utils.video_utils import create_thumbnail_local_video, create_video_hash
from utils.video_utils import create_video_obj_from_file

json_file = "./z_data/oximeter.json"

data = json.load(open(json_file, 'r'))

# video_filepath = data.get("video_filepath", None)
video_filepath = "./z_data/videos/oximeter.mp4"
if video_filepath:
    video_hash = create_video_hash(video_filepath)
    video_obj = VideoUrl.objects.filter(video_hash=video_hash).first()
    if not video_obj:
        thumbnail = create_thumbnail_local_video(video_filepath)
        video_obj = create_video_obj_from_file(
            video_filepath, video_hash, thumbnail)

    name = data.get('name', None)
    media_obj, _ = KpMediaInfo.objects.update_or_create(
        video_url=video_obj, defaults={"media_type": MEDIA_TYPE_VIDEO, "name": name})

    MediaButtonMapping.objects.filter(media=media_obj).delete()
    butttons = data.get('buttons', [])
    for button in butttons:
        action = button.get('action', None)
        action_type = action.get('type', None)
        action_data = action.get('data', None)
        action_obj = create_action_object(action_type, action_data)
        print(action_obj)

        start = button.get('start', None)
        end = button.get('end', None)
        name = button.get('name', None)
        bbox = button.get('bbox', None)
        shape = button.get('shape', None)
        pauseVideo = button.get('pauseVideo', None)
        background_img = button.get('background_img', None)

        bbox_obj = create_bbox_obj(bbox)
        button_obj = ButtonData.objects.create(
            name=name,
            start=start,
            end=end,
            bbox=bbox_obj,
            shape=shape,
            pause_video_dur=pauseVideo,
            background_img=background_img,
            action_id=action_obj
        )

        MediaButtonMapping.objects.get_or_create(
            media=media_obj, button=button_obj)
    print(media_obj)
