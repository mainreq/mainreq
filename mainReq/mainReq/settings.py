"""
Django settings for mainReq project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '@&c9(e+0kk=0b%@3&-ri@ei^1v4xgq#011bjs4k!x)f041*70v'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'reqApp',
    'tinymce',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'mainReq.urls'

WSGI_APPLICATION = 'mainReq.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases
from reqApp.db_conf import *
"""
IMPORTANT ! ! ! ! ! ! ! ! ! ! ! ! ! ! !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
TODO when deploy:

Create /reqApp/db_conf.py (with following custom (NAME, USER, PASSWORD) lines)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': '____________',
        'USER': '____________',
        'PASSWORD': '____________',
        'HOST': 'localhost',   # Or an IP Address that your DB is hosted on
        'PORT': '3306',
    }
}
"""

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Chile/Continental'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# login/logout
LOGIN_URL = 'reqApp:login'
LOGIN_REDIRECT_URL = 'reqApp:PR' # selectProject.html
LOGOUT_URL = 'reqApp:login'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

TEMPLATE_DIRS = [os.path.join(BASE_DIR, 'templates')]

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages',
    "django.core.context_processors.media",
    'django.core.context_processors.static',
)

# Tiny-mce
TINYMCE_JS_URL = os.path.join(STATIC_URL, "js/tiny_mce/tiny_mce.js")
TINYMCE_JS_ROOT = os.path.join(STATIC_URL, "tiny_mce/")

# doc. img. upload folder
IMAGES_UPLOAD = MEDIA_ROOT + '/uploads/'

# email
from reqApp.email_settings import *
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
"""
IMPORTANT ! ! ! ! ! ! ! ! ! ! ! ! ! ! !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
TODO when deploy:

Create /reqApp/email_settings.py (with following custom lines)

EMAIL_HOST_USER = '_______@gmail.com' # your gmail
EMAIL_HOST_PASSWORD = '________' # your gmail password
ADMINS = (('Homero', '______@gmail.com'),) # (optional) send errors stacktrace by email
"""
