# Statement for enabling the development environment
import os

DEBUG = True

# Define the application directory


BASE_DIR = os.path.abspath(os.path.dirname(__file__))

_DEFAULT_URI = 'sqlite:///' + os.path.join(os.path.abspath('.'), 'SpiderKeeper.db')
SQLALCHEMY_DATABASE_URI = os.getenv('SK_DATABASE_URI', _DEFAULT_URI)
SQLALCHEMY_TRACK_MODIFICATIONS = False
DATABASE_CONNECT_OPTIONS = {}

# Application threads. A common general assumption is
# using 2 per available processor cores - to handle
# incoming requests using one and performing background
# operations using the other.
THREADS_PER_PAGE = 2

# Enable protection agains *Cross-site Request Forgery (CSRF)*
CSRF_ENABLED = True

# Use a secure, unique and absolutely secret key for
# signing the data.
CSRF_SESSION_KEY = "36a372e9c1988acc04d12ea92f194a2a8f4b6e2c"

# Secret key for signing cookies
SECRET_KEY = "72e2fc5300409e20fda661734ceb03a3d6d72d50"

# log
LOG_LEVEL = 'INFO'

# spider services
_DEFAULT_SERVER = 'http://localhost:6800'
SERVER_TYPE = 'scrapyd'
SERVERS = os.getenv('SK_SERVERS', _DEFAULT_SERVER).split(',')

# basic auth
NO_AUTH = False
BASIC_AUTH_USERNAME = os.getenv('SK_USERNAME', 'admin')
BASIC_AUTH_PASSWORD = os.getenv('SK_PASSWORD', 'admin')
BASIC_AUTH_FORCE = True
