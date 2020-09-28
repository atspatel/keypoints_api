# from popup_ops.models import KpMediaInfo
# from playlist_ops.models import MediaInfo, PlaylistMediaMapping

# all_media = MediaInfo.objects.all()

# for media in all_media:
#     kp_obj, _ = KpMediaInfo.objects.get_or_create(
#         id=media.id,
#         defaults={
#             "media_type": media.media_type,
#             "video_url": media.video_url,
#             "audio_url": media.audio_url,
#             "language": media.language
#         })
#     print(kp_obj.id, media.id)

# all_mapping = PlaylistMediaMapping.objects.all()

# for mapping in all_mapping:
#     media = mapping.media

#     kp_obj = KpMediaInfo.objects.filter(id=media.id).first()
#     print(kp_obj.id, media.id)

#     mapping.kp_media = kp_obj
#     mapping.button = media.button
#     mapping.title = media.title
#     mapping.save()
