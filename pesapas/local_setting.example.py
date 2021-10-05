import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATABASES = {
    'default': {
        'ENGINE': '',
        'NAME': ''
    }
}

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': '',
    },
}

EMAIL_BACKEND = ''

STATIC_URL = '/assets/'

MEDIA_URL = '/media/'

STATIC_ROOT = os.path.join(BASE_DIR, 'assets')

MEDIA_ROOT = os.path.join(BASE_DIR, 'pesapas/media')
