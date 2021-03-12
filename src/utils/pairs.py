from utils.tickers import get_tickers_info
import json, logging


logger = logging.getLogger(__name__)


def parser(data, cur, coin):
    tickers = [
        t for t in data if t['cur'] == cur.upper() and t['coin'] == coin.upper()
    ]
    logger.debug(tickers)
    return tickers


def get_pair_info(exchange_name, cur, coin):
    logger.info('Getting {}-{} current data for {}.'.format(cur, coin, exchange_name))
    return parser(get_tickers_info(exchange_name), cur, coin)