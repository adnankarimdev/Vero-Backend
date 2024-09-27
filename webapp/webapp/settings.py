"""
Django settings for webapp project.

Generated by 'django-admin startproject' using Django 5.1.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-y^#=%lxy#+mt4v0kvvperrim1&82h5h4q1w6@z33_4q9+&wtt)"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DJANGO_DEBUG", "True") == "True"

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "10.0.0.239",
    "192.168.1.226",
    "e79f-2604-3d09-1c77-8cb0-61dc-c59a-c01b-4aac.ngrok-free.app",
    "vero.ngrok.dev",
    "vero.ec2.ngrok.app",
    "3.137.148.202",
    "3.134.83.89",
    "18.116.234.208",
    "ec2-18-116-234-208.us-east-2.compute.amazonaws.com",
    "52.14.232.28",  # t3.medium new ip ec2
    "ec2-52-14-232-28.us-east-2.compute.amazonaws.com",  # t3.medium new web add ec2
    "ec2-3-137-148-202.us-east-2.compute.amazonaws.com",
    "3.12.68.212",  # elastic ip vero server
    "ec2-3-12-68-212.us-east-2.compute.amazonaws.com",  # elastic dns vero server
    "vero-io.com",
    "www.vero-io.com",
]

GOOGLE_MAPS_API_KEY = "AIzaSyDEJBvbJXfBOqam_dohKIp-9OT6ZBYB2rY"

AUTH_USER_MODEL = "backend.CustomUser"

# Application definition

INSTALLED_APPS = [
    "corsheaders",
    "backend",
    "rest_framework",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:4000",  # If you want to allow requests from your local environment
    "http://localhost:4100",
]

CORS_ALLOW_HEADERS = [
    "content-type",
    "authorization",
    "x-requested-with",
]


ROOT_URLCONF = "webapp.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "webapp.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.sqlite3",
#         "NAME": BASE_DIR / "db.sqlite3",
#     }
# }


# Check if we're in production or local
if os.getenv("ENV_DATABASE") == "PROD":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("PROD_DB_NAME"),
            "USER": os.getenv("PROD_DB_USER"),
            "PASSWORD": os.getenv("PROD_DB_PASSWORD"),
            "HOST": os.getenv("PROD_DB_HOST"),
            "PORT": os.getenv("PROD_DB_PORT"),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("LOCAL_DB_NAME"),
            "USER": os.getenv("LOCAL_DB_USER"),
            "PASSWORD": os.getenv("LOCAL_DB_PASSWORD"),
            "HOST": os.getenv("LOCAL_DB_HOST"),
            "PORT": os.getenv("LOCAL_DB_PORT"),
        }
    }

# LOCAL
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'vero-test',  # Replace with your database name
#         'USER': 'postgres',  # Replace with your database user
#         'PASSWORD': 'veroadmin',  # Replace with your user's password
#         'HOST': 'localhost',  # Default host for local PostgreSQL
#         'PORT': '5433',  # Default PostgreSQL port
#     }
# }

# PROD
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'veroprod',  # Replace with your database name
#         'USER': 'postgres',  # Replace with your database user
#         'PASSWORD': 'veroadmin',  # Replace with your user's password
#         'HOST': 'database-test-vero.cx8im6akuajo.us-east-2.rds.amazonaws.com',  # Default host for local PostgreSQL
#         'PORT': '5432',  # Default PostgreSQL port
#     }
# }

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
