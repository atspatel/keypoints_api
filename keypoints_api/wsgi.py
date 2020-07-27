"""
WSGI config for keypoints_api project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/howto/deployment/wsgi/
"""


import os
import json
from django.core.wsgi import get_wsgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'keypoints_api.settings') ## line ref

## Check settings in imported after setting in os env (line ref), autosave will push this up.
## turn off autosave before savingg this

from django.conf import settings
config = json.load(open(os.path.join(BASE_DIR, 'config.json'), 'r'))
os.environ.setdefault('GOOGLE_APPLICATION_CREDENTIALS',
                      config.get('GOOGLE_APPLICATION_CREDENTIALS', None))

application = get_wsgi_application()
