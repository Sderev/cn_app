# SECURITY WARNING: don't run with debug turned on in production!
import os

# Turn off in production environment
DEBUG = True

# Website
ALLOWED_HOSTS = ['localhost.localdomain', '127.0.0.1']

# SQLite conf
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        # for production give absolute path when using sqlite3
        'NAME': 'db.sqlite'
    }
}

# Example with PostGreSQL
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql_psycopg2',
#         'NAME': 'dbname',
#         'USER': 'dbuser',
#         'PASSWORD': 'dbpassword',
#         'HOST': 'localhost',
#         'PORT': '',
#     }
# }


# URL for static and data resources
STATIC_URL = "/static/"
DATA_URL = "http://example.com/cnapp_data/"

# For a prod env, give absolute paths to folders writable by web server user
DATA_DIR = '/path/to/repo-data'
# For a dev env, DATA_DIR may be inside src folder
# DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
#                         'repo-data')


REPOS_DIR = os.path.join(DATA_DIR, 'repositories')
GENERATED_SITES_DIR = os.path.join(DATA_DIR, 'sites')
GENERATED_SITES_URL = os.path.join(DATA_URL, 'sites')


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'agoodsecretkey'

# In a production environment, make sure to give a
# filename writable by web server
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        'apps_handler': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'debug.log', 
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
        },
        'escapad': {
            'handlers': ['apps_handler'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
        },
    },
}

