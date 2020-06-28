from tags_models.models import KeypointsCategoryTag, LanguageTag
from utils.text_utils import text_to_query
from accounts.models import User

# LanguageTag.objects.all().delete()
# KeypointsCategoryTag.objects.all().delete()

categories = [['Explore', 1], ['Politics', 2], ['World', 3], [
    'Sports', 4], ['Teh', 5], ['Markets', 6], ['Entertainment', 7]]
languages = [['English', 1], ['Hindi', 1]]

user_obj = User.objects.filter(phone='8953457318').first()
for c, i in categories:
    key = text_to_query(c)
    obj, _ = KeypointsCategoryTag.objects.update_or_create(
        key=key, defaults={"tag": c, 'index': i, 'created_by': user_obj})

for c, i in languages:
    key = text_to_query(c)
    obj, _ = LanguageTag.objects.update_or_create(
        key=key, defaults={"tag": c, 'created_by': user_obj})
