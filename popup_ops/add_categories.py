from popup_ops.models import ActionTag, PopupTag
from utils.text_utils import text_to_query

action = ['changeVideo', 'changeAudio',
          'openUrl', 'download', 'seekTo', 'openPopup']

popup = ['mediaCarousel', 'html']


for a in action:
    key = text_to_query(a)
    tag = a

    ActionTag.objects.update_or_create(key=key, defaults={"tag": tag})


for a in popup:
    key = text_to_query(a)
    tag = a

    PopupTag.objects.update_or_create(key=key, defaults={"tag": tag})
