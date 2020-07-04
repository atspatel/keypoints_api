from tags_models.models import KeypointsCategoryTag, LanguageTag
from utils.text_utils import text_to_query
from accounts.models import User

# LanguageTag.objects.all().delete()
# KeypointsCategoryTag.objects.all().delete()

categories = [['Explore', 1, 'https://storage.googleapis.com/kp_videos/app_icons/explore.png'],
              ['Politics', 2, 'https://storage.googleapis.com/kp_videos/app_icons/politics.png'],
              ['World', 3, 'https://storage.googleapis.com/kp_videos/app_icons/world.png'],
              ['Sports', 4, 'https://storage.googleapis.com/kp_videos/app_icons/sports.png'],
              ['Tech', 5, 'https://storage.googleapis.com/kp_videos/app_icons/tech.png'],
              ['Markets', 6, 'https://storage.googleapis.com/kp_videos/app_icons/market.png'],
              ['Entertainment', 7, 'https://storage.googleapis.com/kp_videos/app_icons/entertainment.png']]
languages = [['English', 1], ['Hindi', 1]]

user_obj = User.objects.filter(phone='8953457318').first()
for c, i, thumbnail in categories:
    key = text_to_query(c)
    obj, _ = KeypointsCategoryTag.objects.update_or_create(
        key=key, defaults={"tag": c, 'index': i, 'thumbnail_img': thumbnail, 'created_by': user_obj})

for c, i in languages:
    key = text_to_query(c)
    obj, _ = LanguageTag.objects.update_or_create(
        key=key, defaults={"tag": c, 'created_by': user_obj})
