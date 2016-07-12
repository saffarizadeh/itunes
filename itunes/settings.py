import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = 'k&3o$wg)z5^^z&75j1rb_og(e58)dnks1il+zjubsww4oh6(p('

DEBUG = False

INSTALLED_APPS = (
    'app',
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'itunes_lp',
        'USER': 'postgres',
        'PASSWORD': 'linux116',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'EST'

USE_I18N = True

USE_L10N = True

USE_TZ = False
