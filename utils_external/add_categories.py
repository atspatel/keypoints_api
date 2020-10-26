from popup_ops.models import ActionTag, PopupTag, AspectRatio
from utils.text_utils import text_to_query
from constants import storage_dir

action = ['changeVideo', 'changeAudio',
          'openUrl', 'download', 'seekTo', 'openPopup']

popup = ['mediaCarousel', 'html']

aspect_ratio = [
    {
        "ratio_s": "9:16",
        "ratio": 9 / 16,
        "image": "%s/ratio/9x16.png" % (storage_dir),
        "size": {"width": 720, "height": 1280}
    },
    {
        "ratio_s": "4:5",
        "ratio": 4 / 5,
        "image": "%s/ratio/4x5.png" % (storage_dir),
        "size": {"width": 720, "height": 900}
    },
    {
        "ratio_s": "1:1",
        "ratio": 1,
        "image": "%s/ratio/1x1.png" % (storage_dir),
        "size": {"width": 1080, "height": 1080}
    },
    {
        "ratio_s": "4:3",
        "ratio": 4 / 3,
        "image": "%s/ratio/4x3.png" % (storage_dir),
        "size": {"width": 1024, "height": 768}
    },
    {
        "ratio_s": "16:9",
        "ratio": 16 / 9,
        "image": "%s/ratio/16x9.png" % (storage_dir),
        "size": {"width": 1280, "height": 720}
    }
]


for a in action:
    key = text_to_query(a)
    tag = a

    ActionTag.objects.update_or_create(key=key, defaults={"tag": tag})


for a in popup:
    key = text_to_query(a)
    tag = a

    PopupTag.objects.update_or_create(key=key, defaults={"tag": tag})

for a in aspect_ratio:
    ratio_s = a['ratio_s']
    ratio = a["ratio"]
    image = a['image']
    width = a['size']['width']
    height = a['size']['height']

    ratio_obj, _ = AspectRatio.objects.update_or_create(
        ratio=ratio, defaults=dict(ratio_s=ratio_s, image=image, width=width, height=height))
    print(ratio_obj.id, ratio)
