from distutils.util import strtobool
from pathlib import Path
import django.db.models.options as options
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

options.DEFAULT_NAMES = options.DEFAULT_NAMES + ('search_fields',)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = strtobool(os.environ.get('DEBUG'))

ALLOWED_HOSTS = ['*']

DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL')

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

AUTH_USER_MODEL = 'BAapp.MyUser'

# Application definition

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'crispy_forms',
    'BAapp',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

# Choose db config depending on the environment
db_conf = str(BASE_DIR.joinpath('config/mariadb.conf'))
if strtobool(os.environ.get("DOCKER")):
    db_conf = str(BASE_DIR.joinpath('config/mariadb-docker.conf'))


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'OPTIONS':{
            'read_default_file': db_conf
        },
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'es-ar'

TIME_ZONE = 'America/Buenos_Aires'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# Login

LOGIN_REDIRECT_URL = 'router'
LOGOUT_REDIRECT_URL = 'home'

# Media

MEDIA_URL = '/media/'

# SITE_ID (this is for getting full url in models)

SITE_ID = 1

# When DEBUG is set to False

if not DEBUG:
    # SECURE_SSL_REDIRECT = True

    # Allowed hosts genera bad request 400
    # ALLOWED_HOSTS = ["bvagro.com.ar", "clientes.bvagro.com.ar"]

    EMAIL_BACKEND = 'django_ses.SESBackend'
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
