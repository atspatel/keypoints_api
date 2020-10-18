import json
from popup_ops.models import ButtonData, ButtonInstance
from popup_ops.action_utils import create_action_object

from popup_ops.serializers import ButtonInstanceSerializer

json_file = "./z_data/button_data.json"

data = json.load(open(json_file, 'r'))

button = data.get('button_obj', None)

button_id = button.get('id', None)
name = button.get('name', None)
title = button.get('title', None)
shape = button.get('shape', None)
background_img = button.get('bg_image', None)
style = button.get('button_style', None)


button_obj, _ = ButtonData.objects.update_or_create(id=button_id, defaults={
    "name": name,
    "title": title,
    "shape": shape,
    "background_img": background_img,
    "style": style
})


action = data.get('action', None)

action_type = action.get('type', None)
action_data = action.get('data', None)
action_obj = create_action_object(action_type, action_data)

id = data.get('id', None)
time = data.get('time', None)

transform = data.get('transform', None)
start = time.get('start', None)
end = time.get('end', None)

button_instance_obj, _ = ButtonInstance.objects.update_or_create(id=id, defaults={
    "button_obj": button_obj,
    "start": start,
    "end": end,
    "transform": transform,
    "action_id": action_obj,
})


print(ButtonInstanceSerializer(button_instance_obj).data)
