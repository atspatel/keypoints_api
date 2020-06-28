import os
import ffmpeg_streaming
from ffmpeg_streaming import Formats
from ffmpy import FFmpeg

from django.core.files.storage import default_storage
from django.core.files import File

from urllib.parse import urljoin
from django.conf import settings
import hashlib

BASE_DIR = "./z_data/videos/"
if not os.path.isdir(BASE_DIR):
    os.makedirs(BASE_DIR)


def compress_video(finput):
    _, video_file_name = os.path.split(finput)
    video_base_name = video_file_name.rsplit('.', 1)[0]
    output_folder = os.path.join(BASE_DIR, video_base_name)
    if not os.path.isdir(output_folder):
        os.makedirs(output_folder)

    f_compressed = os.path.join(
        output_folder, "%s_c.mp4" % video_base_name)

    f_original = finput
    if not os.path.isfile(f_compressed):
        ff = FFmpeg(inputs={finput: None}, outputs={
                    f_compressed: '-vcodec libx265 -crf 28'})
        (stdout, stderr) = ff.run()
        return f_original, f_compressed
    else:
        return f_original, f_compressed


def convert_to_hls_video(finput):
    path, filename = os.path.split(finput)
    video_base_name = filename.rsplit('.', 1)[0]
    foutput = os.path.join(path, "%s.m3u8" % video_base_name)

    video = ffmpeg_streaming.input(finput)
    hls = video.hls(Formats.h264(), hls_list_size=0, hls_time=5)
    hls.auto_generate_representations([480, 360, 240], include_original=False)
    hls.output(foutput)
    return path, foutput


def compress_and_hls_video(finput):
    f_original, f_compressed = compress_video(finput)
    print('-- here --', f_original, f_compressed)
    return f_original, f_compressed, convert_to_hls_video(f_compressed)


def upload_file(file_path, name, path="videos"):
    print('uploading........', file_path)
    file_path = default_storage.save(
        "%s/%s" % (path, name), File(open(file_path, 'rb')))
    file_url = urljoin(settings.GS_STATIC_URL, file_path)
    return file_url


def upload_folder():
    pass


if __name__ == "__main__":
    finput = "./z_data/videos/video_6a39022e-d0c1-4bd7-9854-4aa4d8bfbe01.mp4"
    compress_and_hls_video(finput)
