"""
Django settings for FrexTTest project.

Generated by 'django-admin startproject' using Django 3.0.5.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '1@#dw5ut=#m3p+*e1x=^6s8p3rh!q42p2@j$_#9&h_0u_y1wzl'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ["*"]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'captcha',
    'Login',
    'Home',
    'Suggestion',
    'Compile',
    'Judge',
    'Simulate',
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

ROOT_URLCONF = 'FrexTTest.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'FrexTTest.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'frext_test',
        'USER': 'FrexT',
        'PASSWORD': 'FrexT103!',
        'HOST': 'rm-bp1fx85st221svg1r0o.mysql.rds.aliyuncs.com',
        'PORT': '3306',
        'TEST': {
            'NAME': 'frext_test',
            'CHARSET': 'utf8',
            'COLLATION': 'utf8_general_ci'
        }
    }
    # 'default': {
    #     'ENGINE': 'django.db.backends.sqlite3',
    #     'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    # }
}

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'zh-Hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True

SESSION_COOKIE_NAME = "frext"

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/


STATIC_ROOT = os.path.join(BASE_DIR, "/static/")
# STATIC_ROOT = "/mnt/hgfs/0Web/exoticTest/static/"
# STATIC_ROOT = "/home/exotic/exotic/exoticTest/static/"
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

# Exotic Test path configurations
# Please
testFilesPath = "files/testFiles/"
userFilesPath = "files/userFiles/"
compileZipPath = "/tmp/zip/"
compileBitPath = "/tmp/bit/"
compileErrPath = "/tmp/comErr/"
# compileUrl = "http://10.14.30.15:9000/compilefile/"

Rabbit_MQ_IP = "rabbit-mq"
Rabbit_MQ_Port = 5672
Rabbit_MQ_USER = "frext"
Rabbit_MQ_PASS = "zetong103!"
Rabbit_MQ_VHOST = "frext"
Rabbit_MQ_QueueID_Compile = "FrexTCompile01"
Rabbit_MQ_QueueID_Judge = "FrexTJudge01"

Socker_Server_IP = "frext-socket-svc"
Socker_Server_Port = 8040

Compile_MAX_Time = 1200  # ???
Compile_Time_Unit = 5  # ???
Compile_MAX_Thread = 4  # ?????????????????????????????????
Judge_MAX_Time = 1200  # ???
Judge_Time_Unit = 5  # ???
Judge_MAX_Thread = 1  # ?????????????????????

Compile_Server_Url = "http://frext-compile-svc:8012/"
Compile_Server_Api = "compile/"

Simulate_Server_Url = "http://fpga-resim-svc:5000/"
Simulate_Server_Api = "sim/get_all"

# Judge_Server_Url = "http://192.168.80.150:31462/"
# Judge_Server_Api = "judge/"

request_success = "OK"
request_failed = "FAILED"

ROOT_PATH_PRODUCT = "/data/FrexT"
ROOT_PATH_DEVELOP = "./tmp"
