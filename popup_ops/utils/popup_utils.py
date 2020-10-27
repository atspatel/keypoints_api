import uuid
import constants
import logging

from popup_ops.models import KpMediaInfo, AspectRatio
from popup_ops.models import PopupData, PopupInstance, PopupCarouselMapping, PopupTag, Bbox
from popup_ops.serializers import MediaSerializers, AspectRatioSerializer
from popup_ops.serializers import PopupInstanceSerializer, PopupInstanceMiniSerializer
from media_ops.models import ImagesUrl

from utils.text_utils import text_to_query


def create_popup_object(popup_obj_info):
    popup_obj_id = popup_obj_info.get('id', None)
    if(popup_obj_id):
        PopupData.objects.filter(id=popup_obj_id).delete()

    popup_type = popup_obj_info.get('type', None)
    aspect_ratio = popup_obj_info.get('aspect_ratio', {})

    popupTag_obj = PopupTag.objects.filter(
        key=text_to_query(popup_type)).first()
    aspect_ratio_obj = AspectRatio.objects.filter(
        id=aspect_ratio.get('id', None)).first() if aspect_ratio else None

    popup_obj = PopupData.objects.create(
        id=popup_obj_id if popup_obj_id else uuid.uuid4(),
        name=popup_obj_info.get('name', None),
        popup_type=popupTag_obj,
        aspect_ratio=aspect_ratio_obj,
        show_overlay_button=popup_obj_info.get('showOverlayButton', False),
        show_close_button=popup_obj_info.get('showCloseButton', True),
        in_duration=popup_obj_info.get('inDuration', 1.0)
    )
    return popup_obj


def get_or_create_popup_obj(popup_obj_info):
    popup_obj = None
    id = popup_obj_info.get('id', None)
    if(id):
        popup_obj = PopupData.objects.filter(id=id).first()

    if popup_obj:
        return popup_obj
    return create_popup_object(popup_obj_info)


def create_popup_instance_obj(popup):
    popup_obj_info = popup.get('popup_obj', {})
    popup_obj = get_or_create_popup_obj(popup_obj_info)

    popup_id = popup.get('id', None)
    bbox = popup.get(
        'bbox', {'top': 0.05, 'left': 0.05, 'width': 0.9, 'height': 0.9})
    bbox_obj, _ = Bbox.objects.get_or_create(
        top=bbox.get('top', 0.05),
        left=bbox.get('left', 0.05),
        width=bbox.get('width', 0.9),
        height=bbox.get('height', 0.9)
    )

    if(popup_id):
        PopupInstance.objects.filter(id=popup_id).delete()

    popup_instance_obj = PopupInstance.objects.create(
        id=popup_id if popup_id else uuid.uuid4(),
        name=popup.get('name', None),
        popup_obj=popup_obj,
        bbox=bbox_obj,
        pause_video=popup.get('pauseVideo', False)
    )

    data = popup.get('data', [])
    if(len(data) > 0):
        for i, media_data in enumerate(data):
            kp_obj = None
            if(media_data.get('media_type') == 'image'):
                media = media_data.get('media', {})
                url = media.get('src', None)
                image_obj = ImagesUrl.objects.get(
                    image_url=url) if url else (None, None)
                media_obj, _ = KpMediaInfo.objects.get_or_create(
                    image_url=image_obj,
                    defaults={
                        'media_type': constants.MEDIA_TYPE_IMAGE
                    }) if image_obj else (None, None)
            PopupCarouselMapping.objects.update_or_create(
                popup_id=popup_instance_obj, media=media_obj, defaults={'index': i})
    return popup_instance_obj


def get_popup_instance_obj(popup):
    popup_id = popup.get('id', None)
    if(popup_id):
        return PopupInstance.objects.filter(id=popup_id).first()
    return None


def get_or_create_popup_instance_obj(popup):
    popup_instance_obj = None
    popup_instance_obj = get_popup_instance_obj(popup)
    if popup_instance_obj:
        return popup_instance_obj
    return create_popup_instance_obj(popup)
