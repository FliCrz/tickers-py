import importlib, json, time, logging
import libs


logger = logging.getLogger(__name__)


def get_tickers_info(exchange_name):
    """Get tickers data from exchange, add the timestamp to it and append
    it to a list.

    params:
      exchange_name:
        - The name of a supported exchange (see get_exchanges()) to fetch data from.
    returns:
      - A list of tickers for the exchange.
    """
    tickers = []
    logger.info('Getting tickers for {}'.format(exchange_name))
    module = importlib.import_module('libs.{}'.format(exchange_name))
    for i in module.run():
        if i != None:
            i['timestamp'] = time.time()
            logger.debug(i)
            tickers.append(i)
            # yield i
        else:
            logger.error(i)
    logger.info('All tickers fetched.')
    logger.debug(tickers)
    return tickers