"""
Django settings for mysite project.

Generated by 'django-admin startproject' using Django 2.0.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'qgjkwca^dcx!4xqoo7%r-o&#fh$0nnms8wt%fd*z^%npym_nwl'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'ckeditor',
    'ckeditor_uploader',
    'blog',
    'read_statistics',
    'comment',
    'likes',
    'user',
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

ROOT_URLCONF = 'mysite.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
        ],
        # 这个设置的目的就是让模板引擎去APP的目录中找模板文件
        'APP_DIRS': True,

        'OPTIONS': {
            # 下面是django自带的默认模板，包括方法
            'context_processors': [
                'django.template.context_processors.debug',
                # django自带返回request,前端页面可以直接调用
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # 自定义方法，返回登录form表单
                'user.context_processors.login_modal_form',
            ],
        },
    },
]

WSGI_APPLICATION = 'mysite.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.0/topics/i18n/
# 文字类型不太适合大写'zh-Hans'，转换成小写'zh-hans'，解决ckeditor编辑框上汉字是繁体字的问题
LANGUAGE_CODE = 'zh-hans'

# TIME_ZONE = 'UTC'
TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

# 如果不需要使用时区就设置为False，需要使用时区的话就设置为True，本项目中是需要使用的
# 设置为False的话，对于windows系统不好使，存入数据库中的还是UTC
# 但USE_TZ = True，TIME_ZONE = 'Asia/Shanghai' 存入数据库中的是当前北京时间，有点晕
# 存入数据库的是当前时间，但是它生成并返回的时间是utc????
USE_TZ = True

# 静态文件
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

# 设置静态文件的存放地址，方便引用
# 已经存在的是指向APP应用的
STATIC_URL = '/static/'

# 自定义static文件
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static')
]

# 自定义参数
EACH_PAGE_BLOGS_NUMBER = 5

# media配置
MEDIA_URL = '/media/'
# 存放上传的文件的地址
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# 配置ckeditor
# 将图片上传到项目mysite下面的media/upload/ 路径下
CKEDITOR_UPLOAD_PATH = 'upload/'


# forms表单的 富文本编辑框设置ckeditor
CKEDITOR_CONFIGS = {
    'default': {},
    'comment_ckeditor': {
        'toolbar': 'custom',
        'toolbar_custom': [
            ['Bold', 'Italic', 'Underline', 'Strike', 'Subscript', 'Superscript'],
            ["TextColor", "BGColor", 'RemoveFormat'],
            ['NumberedList', 'BulletedList'],
            ['Link', 'Unlink'],
            ["Smiley", "SpecialChar", 'Blockquote'],
        ],
        'width': 'auto',
        'height': '180',
        'tabSpaces': 4,
        'removePlugins': 'elementspath',
        'resize_enabled': False,
    }
}


# 自定义数据库缓存设置，后台服务器缓存，暂时保存数据
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'my_cache_table'
    }
}


# 发送email设置，使用QQ邮箱
# https://docs.djangoproject.com/en/2.0/ref/settings/#email
# https://docs.djangoproject.com/en/2.0/topics/email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.qq.com'
EMAIL_PORT = 25   # 发送端口
EMAIL_HOST_USER = '2462971145@qq.com'  # 发件人
EMAIL_HOST_PASSWORD = 'ehnqdhuvxpgtdhig'   # 授权码，登录QQ邮箱官网 获取 mail.qq.com
EMAIL_SUBJECT_PREFIX = '[殷爽爽的博客]'   # 邮件的前缀
EMAIL_USE_TLS = True  # 与SMTP服务器通信时，是否启动TLS链接（安全链接）


"""
（1）settings中已经设定的路径啥的都是指向APP应用的，是APP应用下的，
文件可以直接写相对路径就可以，不需要写绝对路径，什么templates啥的，
settings中设定了的, 是会自动找app下面的static及templates的，直接写你要找的模板或者css就行
不过css的书写格式 和html有区别    
默认： <link rel="stylesheet" href="{% static  'base.css'%}">
自定义：<link rel="stylesheet" href="/static/base.css">  不能只写base.css，首先形式得是个地址吧。

（2） 'APP_DIRS': True:
这个设置的目的就是让模板引擎去APP的目录中找模板文件, 但是你创建的模板文件夹名字一定要是templates
    
(3)STATIC_URL = '/static/':
同上，会自动去APP的static文件夹中寻找静态文件，文件夹名字也一定要是stativ

(4) 'DIRS': [os.path.join(BASE_DIR, 'templates'),],
这里可以添加你的自定义目录，下面的也是
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
django中会按照顺序查询模板及static文件夹，先找APP,然后找自定义。
"""
