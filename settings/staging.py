import os
import logging

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

# Log configuration
LOG_LEVEL = logging.DEBUG
USE_SYSLOG = False
SYSLOG_TAG = "lannister.dev"
SYSLOG_FACILITY = logging.handlers.SysLogHandler.LOG_LOCAL2

# Affiliate subdomain
AFFILIATE_URL = "aff.jualio.com"