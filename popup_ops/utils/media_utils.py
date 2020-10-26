from constants import *
from popup_ops.models import KpMediaInfo, MediaButtonMapping
from popup_ops.utils.button_utils import create_button_instance_object


def create_media_object(media_info, video_obj=None):
    # TODO :: Create video obj and add audio and image object
    media_obj = None
    media_id = media_info.get("id", None)
    if media_id:
        media_obj = KpMediaInfo.objects.filter(id=media_id).first()

    if not media_obj:
        if video_obj:
            name = media_info.get('name', None)
            media_obj = KpMediaInfo.objects.create(
                video_url=video_obj,
                media_type=MEDIA_TYPE_VIDEO,
                name=name
            )
        else:
            return False

    MediaButtonMapping.objects.filter(media=media_obj).delete()
    butttons = media_info.get('buttons', [])
    for button_instance in butttons:
        button_obj = create_button_instance_object(button_instance)
        mapping_obj = MediaButtonMapping.objects.create(
            media=media_obj, button=button_obj)
    return media_obj
