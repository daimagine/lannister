import os
import logging
from tornado.log import LogFormatter as TornadoLogFormatter


# Add the current directory to the python path
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
LOG_DIR = os.path.join(BASE_DIR, 'logs')

# Specify here the database settings.
DATABASE = {
    'NAME': 'shortlrdb',        # DB name in PostgreSQL
    'HOST': 'localhost',        # Server IP. Default: localhost
    'PORT': '5432',             # PostgreSQL default: 5432
    'USER': 'postgres',         # User that has access to the DB
    'PASSWORD': 'postgres',     # Password for the user
}

# Default version of the API
API_VERSION = 'v1'

# Server configuration
SERVER_PORT = "8000"

# Log configuration
DEBUG_ENABLED = True
LOG_FILE = '%s/%s' % (LOG_DIR, 'lannister.log')
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '[%(process)d: %(levelname).1s %(asctime)s %(module)s:%(lineno)d] '
                    '%(message)s',
            'datefmt': "%Y-%m-%d %H:%M:%S",
        },
        'colored': {
        	'()': TornadoLogFormatter,
            'format': '%(color)s[%(process)d: %(levelname).1s %(asctime)s %(module)s:%(lineno)d]%(end_color)s '
                    '%(message)s',
            'datefmt': "%Y-%m-%d %H:%M:%S",
            'color': True
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'formatter': 'colored',
            'class': 'logging.StreamHandler',
        },
        'rotate_file': {
            'level': 'DEBUG',
            'formatter': 'standard',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'when': 'midnight',
            'filename': LOG_FILE,
            'encoding': 'utf8'
        }
    },
    'loggers': {
        'lannister': {
            'handlers': ['console', 'rotate_file'],
            'level': 'DEBUG',
        },
    }
}

# Affiliate subdomain
AFFILIATE_URL = "http://a.jual.io"
TWEET_HEADLINE_LENGTH = 115
