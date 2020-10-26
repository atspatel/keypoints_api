import json
from popup_ops.models import ButtonData, ButtonInstance
from popup_ops.utils.action_utils import create_action_object


def create_button_object(button):
    button_id = button.get('id', None)
    button_obj, _ = ButtonData.objects.update_or_create(
        id=button_id, defaults=dict(
            name=button.get('name', None),
            title=button.get('title', None),
            shape=button.get('shape', None),
            background_img=button.get('bg_image', None),
            style=button.get('button_style', None)
        ))
    return button_obj


def create_button_instance_object(button_data):
    button = button_data.get('button_obj', {})
    button_obj = create_button_object(button)

    action = button_data.get('action', {})
    action_obj = create_action_object(
        action.get('type', None), action.get('data', {}))

    id = button_data.get('id', None)
    time = button_data.get('time', {})
    ButtonInstance.objects.filter(id=id).delete()
    button_instance_obj = ButtonInstance.objects.create(
        id=id,
        button_obj=button_obj,
        start=time.get('start', None),
        end=time.get('end', None),
        transform=button_data.get('transform', None),
        action_id=action_obj
    )
    return button_instance_obj
