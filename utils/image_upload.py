

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.core.files import File

from urllib.parse import urljoin
from django.conf import settings
import hashlib

from accounts.models import UserImagesUrl
from media_ops.models import ImagesUrl

from PIL import Image
import io
import requests
import json

thumbnail_size = 512, 512


def pil_image_from_url(url):
    response = requests.get(url)
    return Image.open(io.BytesIO(response.content)).convert('RGB')


def upload_external_image_content_string(content_string, name, user=None):
    hash_val = hashlib.md5(content_string).hexdigest()
    image_obj = ImagesUrl.objects.filter(image_hash=hash_val).first()
    if image_obj:
        return image_obj
    else:
        path = default_storage.save(
            "ImageSets/%s" % name, ContentFile(content_string))
        image_url = urljoin(settings.STORAGE_STATIC_URL, path)
        tn_image_url = None
        img = Image.open(io.BytesIO(content_string))
        img.thumbnail(thumbnail_size)

        imgByteArr = io.BytesIO()
        img.save(imgByteArr, format='JPEG')
        tn_content_string = imgByteArr.getvalue()

        tn_path = default_storage.save(
            "thumbnails/%s" % name, ContentFile(tn_content_string))
        tn_image_url = urljoin(settings.STORAGE_STATIC_URL, tn_path)

        image_obj = ImagesUrl(
            created_by=user,
            image_url=image_url,
            image_hash=hash_val,
            media_type="image/external",
            thumbnail_img=tn_image_url
        )
        image_obj.save()
        return image_obj


def upload_image(image_bytes, user=None):
    content_string = image_bytes.read()
    content_type = image_bytes.content_type

    hash_val = hashlib.md5(content_string).hexdigest()
    image_obj = ImagesUrl.objects.filter(image_hash=hash_val).first()
    if image_obj:
        return image_obj
    else:
        path = default_storage.save(
            "ImageSets/%s" % image_bytes.name, ContentFile(content_string))
        image_url = urljoin(settings.STORAGE_STATIC_URL, path)

        tn_image_url = None
        if content_type.split("/",  1)[0] == "image":
            img = Image.open(io.BytesIO(content_string))
            img.thumbnail(thumbnail_size)

            imgByteArr = io.BytesIO()
            img.save(imgByteArr, format='JPEG')
            tn_content_string = imgByteArr.getvalue()

            tn_path = default_storage.save(
                "thumbnails/%s" % image_bytes.name, ContentFile(tn_content_string))
            tn_image_url = urljoin(settings.STORAGE_STATIC_URL, tn_path)

        image_obj = ImagesUrl(
            created_by=user,
            image_url=image_url,
            image_hash=hash_val,
            media_type=content_type,
            thumbnail_img=tn_image_url
        )
        image_obj.save()
        return image_obj


def upload_profile_image(image_bytes):
    content_string = image_bytes.read()
    hash_val = hashlib.md5(content_string).hexdigest()
    image_obj = UserImagesUrl.objects.filter(image_hash=hash_val).first()
    if image_obj:
        return image_obj
    else:
        path = default_storage.save("ProfilePics/%s" %
                                    image_bytes.name, ContentFile(content_string))
        image_url = urljoin(settings.STORAGE_STATIC_URL, path)
        image_obj = UserImagesUrl(
            image_url=image_url,
            image_hash=hash_val,
        )
        image_obj.save()
        return image_obj
