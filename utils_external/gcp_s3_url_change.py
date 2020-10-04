
from accounts.models import UserImagesUrl
from media_ops.models import ImagesUrl, VideoUrl, AudioUrl
from popup_ops.models import OpenUrlData, DownloadData, ButtonData
from tags_models.models import LanguageTag, KeypointsCategoryTag, KeypointsTopicTag


def update_url(url):
    if url and url.startswith('https://storage.googleapis.com/kp_videos'):
        aws_url = url.replace('https://storage.googleapis.com/kp_videos',
                              'https://keypoints-data.s3.ap-south-1.amazonaws.com')
        return aws_url
    return None


all_data = UserImagesUrl.objects.all()
for data in all_data:
    url = data.image_url
    aws_url = update_url(url)
    if aws_url:
        data.image_url = aws_url
        data.save()
        print('UserImagesUrl', data.id)

all_data = ImagesUrl.objects.all()
for data in all_data:
    url = data.image_url
    aws_url = update_url(url)
    if aws_url:
        data.image_url = aws_url
        data.save()
        print('ImagesUrl, image_url', data.id)

    url = data.thumbnail_img
    aws_url = update_url(url)
    if aws_url:
        data.thumbnail_img = aws_url
        data.save()
        print('ImagesUrl, thumbnail_img', data.id)

all_data = VideoUrl.objects.all()
for data in all_data:
    url = data.url
    aws_url = update_url(url)
    if aws_url:
        data.url = aws_url
        data.save()
        print('VideoUrl, url', data.id)

    url = data.thumbnail_img
    aws_url = update_url(url)
    if aws_url:
        data.thumbnail_img = aws_url
        data.save()
        print('VideoUrl, thumbnail_img', data.id)

    url = data.hls_url
    aws_url = update_url(url)
    if aws_url:
        data.hls_url = aws_url
        data.save()
        print('VideoUrl, hls_url', data.id)

    url = data.compressed_url
    aws_url = update_url(url)
    if aws_url:
        data.compressed_url = aws_url
        data.save()
        print('VideoUrl, compressed_url', data.id)


all_data = AudioUrl.objects.all()
for data in all_data:
    url = data.url
    aws_url = update_url(url)
    if aws_url:
        data.url = aws_url
        data.save()
        print('AudioUrl, url', data.id)

    url = data.thumbnail_img
    aws_url = update_url(url)
    if aws_url:
        data.thumbnail_img = aws_url
        data.save()
        print('AudioUrl, thumbnail_img', data.id)


all_data = AudioUrl.objects.all()
for data in all_data:
    url = data.url
    aws_url = update_url(url)
    if aws_url:
        data.url = aws_url
        data.save()
        print('AudioUrl, url', data.id)

    url = data.thumbnail_img
    aws_url = update_url(url)
    if aws_url:
        data.thumbnail_img = aws_url
        data.save()
        print('AudioUrl, thumbnail_img', data.id)


all_data = OpenUrlData.objects.all()
for data in all_data:
    url = data.url
    aws_url = update_url(url)
    if aws_url:
        data.url = aws_url
        data.save()
        print('OpenUrlData, url', data.id)


all_data = DownloadData.objects.all()
for data in all_data:
    url = data.url
    aws_url = update_url(url)
    if aws_url:
        data.url = aws_url
        data.save()
        print('DownloadData, url', data.id)

all_data = ButtonData.objects.all()
for data in all_data:
    url = data.background_img
    aws_url = update_url(url)
    if aws_url:
        data.background_img = aws_url
        data.save()
        print('ButtonData, url', data.id)


all_data = LanguageTag.objects.all()
for data in all_data:
    url = data.thumbnail_img
    aws_url = update_url(url)
    if aws_url:
        data.thumbnail_img = aws_url
        data.save()
        print('LanguageTag, url', data.id)

all_data = KeypointsCategoryTag.objects.all()
for data in all_data:
    url = data.thumbnail_img
    aws_url = update_url(url)
    if aws_url:
        data.thumbnail_img = aws_url
        data.save()
        print('KeypointsCategoryTag, url', data.id)

all_data = KeypointsTopicTag.objects.all()
for data in all_data:
    url = data.thumbnail_img
    aws_url = update_url(url)
    if aws_url:
        data.thumbnail_img = aws_url
        data.save()
        print('KeypointsTopicTag, url', data.id)
