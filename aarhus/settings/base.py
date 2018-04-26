"""
Django settings for aarhus project.

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
SECRET_KEY = '3o!d$yuj@g2o^wb55^(flxnhh60a=*jbaz_ijs&vxl*wtwneoz'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False



# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'autocomplete_light',
    'crispy_forms',
    'notebook'
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
   )

TEMPLATE_CONTEXT_PROCESSORS=("django.contrib.auth.context_processors.auth",
"django.core.context_processors.debug",
"django.core.context_processors.i18n",
"django.core.context_processors.media",
"django.core.context_processors.static",
"django.core.context_processors.tz",
"django.contrib.messages.context_processors.messages",
"django.core.context_processors.request",)

ROOT_URLCONF = 'aarhus.urls'

WSGI_APPLICATION = 'aarhus.wsgi.application'

CRISPY_TEMPLATE_PACK = 'bootstrap3'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases



# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

TEMPLATE_DIRS = (
    '/var/django/aarhus_2/aarhus/templates',
#	'/Users/senmacbook/CloudStation/Aarhus/Code/aarhus/templates'
    )

STATICFILES_DIRS = (
	'/var/django/aarhus_2/aarhus/static_dir',
    '/var/django/aarhus_2/aarhus/templates'
    #'/Users/senmacbook/CloudStation/Aarhus/Code/aarhus/static',
    #'/Users/senmacbook/CloudStation/Aarhus/Code/aarhus/templates'
    )

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

#MEDIA_ROOT = '/Users/sennierer/CloudStation/Aarhus/Code/aarhus/Media'
MEDIA_ROOT = '/var/django/aarhus_2/aarhus/Media'
#STATIC_ROOT = '/Users/sennierer/CloudStation/Aarhus/Code/aarhus/static'
STATIC_ROOT = '/var/django/aarhus_2/aarhus/static'
MEDIA_URL = '/uploads/'
