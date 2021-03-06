"""
Django settings for WebApi_WorkerPlatform project.

Generated by 'django-admin startproject' using Django 3.2.7.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
from socket import gethostname, gethostbyname

BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-9r3nd#pm6vm9g0!272b7!h%sqr3-xcd0qv$&hf(8+nu(=maa3#'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get("DEBUG", "False") == "True"

ALLOWED_HOSTS = [host.strip() for host in os.environ.get("ALLOWED_HOSTS", "*").split(',')]

ALLOWED_HOSTS += [gethostname(), gethostbyname(gethostname())]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'Api.apps.ApiConfig',
    'rest_framework',
    'django_filters',
    'rest_framework.authtoken',
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

ROOT_URLCONF = 'WebApi_WorkerPlatform.urls'
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = '/media/'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'WebApi_WorkerPlatform.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('RDS_NAME', 'WorkerPlatform1'),
        'USER': os.environ.get('RDS_USERNAME', 'postgres'),
        'PASSWORD': os.environ.get('RDS_PASSWORD', 'init1234'),
        'HOST': os.environ.get('RDS_HOSTNAME', '127.0.0.1'),
        'PORT': os.environ.get('RDS_PORT', '5432'),
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, "static")

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Django Rest Framework
REST_FRAMEWORK = {
    "PAGE_SIZE": 10,
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
    ],
    # "DEFAULT_SCHEMA_CLASS": 'rest_framework.schemas.coreapi.AutoSchema'
}

AUTHENTICATION_BACKENDS = ['Api.backends.CustomAuthBackend']

# Django??????????????????

BASE_LOG_DIR = os.path.join(BASE_DIR, "log")  # ????????????
if not os.path.exists(BASE_LOG_DIR):
    os.mkdir(BASE_LOG_DIR)

LOGGING = {
    'version': 1,  # ?????????
    'disable_existing_loggers': False,  # ?????????????????????logger??????
    # ?????????????????????
    'formatters': {
        # ?????????????????????
        'standard': {
            'format': '[%(asctime)s][%(threadName)s:%(thread)d][task_id:%(name)s][%(filename)s:%(lineno)d]'
                      '[%(levelname)s][%(message)s]'
        },
        # ?????????????????????
        'simple': {
            'format': '[%(levelname)s][%(asctime)s][%(filename)s:%(lineno)d]%(message)s'
        },
        # ?????????????????????????????????
        'collect': {
            'format': '%(message)s'
        }
    },
    # ?????????
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    # ?????????
    'handlers': {
        # ???????????????
        'console': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],  # ?????????Django debug???True???????????????????????????
            'class': 'logging.StreamHandler',  #
            'formatter': 'simple'
        },
        # ?????????
        'default': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',  # ???????????????????????????
            'filename': os.path.join(BASE_LOG_DIR, "xxx_info.log"),  # ????????????
            'maxBytes': 1024 * 1024 * 50,  # ???????????? 50M
            'backupCount': 3,  # ??????????????????
            'formatter': 'standard',
            'encoding': 'utf-8',
        },
        # ???????????????????????????
        'error': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',  # ???????????????????????????
            'filename': os.path.join(BASE_LOG_DIR, "xxx_err.log"),  # ????????????
            'maxBytes': 1024 * 1024 * 50,  # ???????????? 50M
            'backupCount': 5,
            'formatter': 'standard',
            'encoding': 'utf-8',
        },
        # ?????????????????????????????????????????????
        'collect': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',  # ???????????????????????????
            'filename': os.path.join(BASE_LOG_DIR, "xxx_collect.log"),
            'maxBytes': 1024 * 1024 * 50,  # ???????????? 50M
            'backupCount': 5,
            'formatter': 'collect',
            'encoding': "utf-8"
        }
    },
    'loggers': {
        # ?????????logger??????????????????
        '': {
            'handlers': ['default', 'console', 'error'],  # ?????????????????????'console'??????
            'level': 'DEBUG',
            'propagate': True,  # ????????????????????????logger??????
        },
        # ?????? 'collect'???logger???????????????
        'collect': {
            'handlers': ['console', 'collect'],
            'level': 'INFO',
        }
    },
}

