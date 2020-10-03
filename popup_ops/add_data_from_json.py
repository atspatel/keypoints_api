import os
import json

from constants import *

from media_ops.models import ImagesUrl, VideoUrl, AudioUrl

from popup_ops.models import ActionTag, PopupTag, Bbox
from popup_ops.models import KpMediaInfo, ButtonData, MediaButtonMapping
from popup_ops.action_utils import create_media_object

from utils.video_utils import create_thumbnail_local_video, create_video_hash
from utils.video_utils import create_video_obj_from_file

json_file = "./z_data/dress1.json"

data = json.load(open(json_file, 'r'))

video_filepath = "./z_data/videos/dress1.mp4"
if video_filepath:
    video_hash = create_video_hash(video_filepath)
    video_obj = VideoUrl.objects.filter(video_hash=video_hash).first()
    if not video_obj:
        thumbnail = create_thumbnail_local_video(video_filepath)
        video_obj = create_video_obj_from_file(
            video_filepath, video_hash, thumbnail)

    media_obj = create_media_object(data, video_obj)
    print(media_obj)
