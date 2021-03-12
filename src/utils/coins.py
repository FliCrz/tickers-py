import requests, logging, time, json
from utils import third_party_url


logger = logging.getLogger(__name__)


def get_one_coin_by_symbol(symbol):
    logger.info('Getting {}.'.format(symbol.upper()))
    coins = get_coins_from_mem()
    if coins == None: return None
    for c in coins:
        print(c)
        if c['symbol'] == symbol.upper():
            logger.debug(c)
            return c


def get_coin_id(symbol, coins):
    for c in coins:
        if c['symbol'] == symbol.upper():
            logger.debug(c)
            return c['id']


def get_coin_list():
    logger.info('Getting coin list.')
    req = requests.get(third_party_url + '/coins')
    if req.status_code == 200:
        logger.info('Success retrieving coin list.')
        rsl = req.json()
    elif req.status_code == 429:
        logger.warning('Too many requests, sleeping 60s')
        time.sleep(60)
        get_coin_list()
    logger.debug(rsl)
    return rsl


def get_coin_info(coin_id):
    counter = 1
    rsp = requests.get('{}/coins/{}'.format(third_party_url, coin_id.lower()))
    c = rsp.json()
    if rsp.status_code == 200:
        reddit = c['links']['reddit'][0] if 'reddit' in c['links'].keys() else None
        rsl = {
            'name' : c['name'],
            'text' : c['description'],
            'website' : c['links']['website'][0] if 'website' in c['links'].keys() else None,
            'git' : c['links']['source_code'][0] if 'source_code' in c['links'].keys() else None,
            'social' : {'reddit': reddit}
        }
        logger.debug(rsl)
        return rsl

    elif rsp.status_code == 429:
        logger.warning('Too many requests, sleeping: {}s'.format(counter * 5))
        time.sleep(int(counter * 5))
        counter += 1
        get_coin_info(coin_symbol, coin_name)