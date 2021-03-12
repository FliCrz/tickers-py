import json, logging
import config

logger = logging.getLogger(__name__)


def get_active_exchanges():
    """Get active exchanges function.

    returns:
        - a generator with all exchanges that are active.
    """
    exchanges = get_exchanges_info()
    active = []
    for e in exchanges:
        if e['active'] == True:
            active.append(e)
    return active


def get_exchanges_info(filename=None):
    """Get exchanges. We load the exchanges from file.

    returns:
        - a list of exchanges.
    """
    exchanges = get_exchanges_from_file(filename)
    return exchanges


def get_exchanges_from_file(filename=None):
    """Get exchanges from file.

    params:
        - filename to load exchanges from. Defaults to config.EXCHANGES_FILENAME.

    returns:
        - a list of all exchanges
    """
    if filename == None:
        logger.warning('No filename provided, using default.')
        filename = config.EXCHANGES_FILENAME
    logger.info('Extracting exchanges from {}'.format(filename))
    exchanges = json.load(open(filename, 'r'))
    logger.debug(exchanges)
    logger.info('Exchanges retrieved.')
    return exchanges
