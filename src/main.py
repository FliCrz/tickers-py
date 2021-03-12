import os
import sys
import logging
import config
from utils.coins import *
from utils.pairs import *
from utils.exchanges import *
from utils.tickers import *


logger = logging.getLogger(__name__)


def help():
    """Function to display help."""
    print('')
    print('exchange_wrappers')
    print('author: ko.ktk@pm.me')
    print('')
    print('python3 main.py <command> <options>')
    print('')
    print('commands:')
    print('-h, --help                           this help screen.')
    print('-e, --exchanges <filename>           get available exchanges.')
    print('                                     optionally provide the exchanges filename.')
    print('-t, --tickers [exchange name]        get current tickers for some exchange.')
    print('-t [exchange name] <currency> <coin> optionally you can pass a currency and coin symbols (in that order).')
    print('-c, --coins [symbol]                 get a list of supported coins from our information provider (coinpaprika).')
    print('                                     optionally you can pass the coin symbol to get its id.')
    print('-i, --info [coin id]                 get coin information, you need to supply the coin-id, use -c with symbol to get it.')
    print('-l, --log [level]                    get logging with level.')
    print('-R, --server                         run flask server and use it as api.')
    print('                                     WARNING: if possible use the docker-compose.yml to spin up all services.')
    print('                                     app will be reachable at address http://localhost:5000.')
    print('')


def run():

    if sys.argv[1] in ['-h', '--help']:
        return help()

    elif sys.argv[1] in ['-e', '--exchanges']:
        if len(sys.argv) > 2:
            ex = get_exchanges_info(str(sys.argv[2]))
        else:
            ex = get_exchanges_info()
        print(ex)
        return ex

    elif sys.argv[1] in ['-t', '--tickers']:
        if len(sys.argv) == 3:
            tickers = []
            for t in get_tickers_info(sys.argv[2]):
                tickers.append(t)
        else:
            tickers = get_pair_info(
                sys.argv[2], sys.argv[3], sys.argv[4]
            )
        print(tickers)
        return tickers


    elif sys.argv[1] in ['-c', '--coins']:
        if len(sys.argv) == 2:
            coins = get_coin_list()
        else:
            coins = get_coin_id(sys.argv[2], coins)
        print(coins)
        return coins

    elif sys.argv[1] in ['-i', '--info']:
        coin = get_coin_info(sys.argv[2])
        print(coin)
        return coin
        

    elif sys.argv[1] in ['-R', '--server']:
        from app import app

        app.run()

    else:
        print('')
        print('Command not found.')
        print('Please check our help page with "./main.py -h".')
        print('')


if __name__ == "__main__":
    run()