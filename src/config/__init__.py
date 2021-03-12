import os
import sys
import logging
import datetime


# Set logging level
for e in range(len(sys.argv)):
    if sys.argv[e] in ['-l', '--log']:
        numeric_level = getattr(logging, sys.argv[e + 1].upper(), None)
        logging.basicConfig(format='%(asctime)s %(levelname)s: %(name)s: %(message)s', level=numeric_level)


logger = logging.getLogger(__name__)


if os.environ.get('API_SERVER_CALLS_TIMEOUT'):
    # Timeouts
    API_SERVER_CALLS_TIMEOUT = int(os.environ.get('API_SERVER_CALLS_TIMEOUT'))
    API_SERVER_NOT_AVAILABLE_TIMEOUT = int(os.environ.get('API_SERVER_NOT_AVAILABLE_TIMEOUT'))

    # Exchanges filename
    EXCHANGES_FILENAME = os.environ.get('EXCHANGES_FILENAME')

    # Cache
    CACHE_TYPE = os.environ.get('CACHE_TYPE')
    CACHE_DEFAULT_TIMEOUT = os.environ.get('CACHE_DEFAULT_TIMEOUT')

else:
    # Timeouts
    API_SERVER_CALLS_TIMEOUT = 2
    API_SERVER_NOT_AVAILABLE_TIMEOUT = 10

    # Schedulers
    EXCHANGES_FILENAME = 'src/Exchanges.json'

    # Cache
    CACHE_TYPE = "simple"
    CACHE_DEFAULT_TIMEOUT = 300
