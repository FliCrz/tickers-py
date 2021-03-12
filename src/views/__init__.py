from flask import jsonify, abort, render_template
from app import app
from utils.coins import *
from utils.pairs import *
from utils.exchanges import *
from utils.tickers import *
from mycache import cache
import config


@app.route('/get_exchanges/<mode>')
@cache.cached(timeout=config.CACHE_DEFAULT_TIMEOUT)
def get_exchanges_view(mode='all'):
    if mode == 'all':
        exchanges = get_exchanges_info()
    elif mode == 'active':
        exchanges = get_active_exchanges()
    return jsonify(exchanges) if exchanges != None else abort(404)


@app.route('/get_coin/<symbol>')
@cache.cached(timeout=config.CACHE_DEFAULT_TIMEOUT)
def get_coin_view(symbol='all'):
    if symbol == 'all':
        coin = get_coins_from_mem()
    else:
        coin = get_one_coin_by_symbol(symbol.upper())
    return jsonify(coin) if coin != None else abort(503)


@app.route('/get_ticker/<exchange>')
@cache.cached(timeout=config.CACHE_DEFAULT_TIMEOUT)
def get_ticker(exchange='all'):
    tickers = []
    if exchange == 'all':
        for e in get_active_exchanges():
            tickers.append(get_tickers_from_mem(e['name'].lower()))
    else:
        tickers = get_tickers_from_mem(exchange.lower())
    return jsonify(tickers) if tickers != None else abort(503)