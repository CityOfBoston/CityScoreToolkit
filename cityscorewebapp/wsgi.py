"""
WSGI config for cityscorewebapp project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/howto/deployment/wsgi/
""" 

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cityscorewebapp.settings")

# application = get_wsgi_application()

#HEROKU
from dj_static import Cling, MediaCling
application = Cling(MediaCling(get_wsgi_application()))

from whitenoise.django import DjangoWhiteNoise
application = DjangoWhiteNoise(application)
