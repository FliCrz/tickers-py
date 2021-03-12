import importlib, sys
import libs
from utils import *


def test_all_wrappers():
    exchanges = get_exchanges_info()
    for e in exchanges:
        test_wrapper_ticker(e['name'])


def test_wrapper_ticker(wrapper_name):
    print('Testing: {}'.format(wrapper_name))
    data = get_tickers_info(wrapper_name)
    for i in data: print(i)


def test_wrapper_balance(wrapper_name, key, secret):
    module = importlib.import_module('libs.{}'.format(wrapper_name))
    data = module.Private(key, secret).get_balances()
    for i in data: print(i)


def test_wraper_create_order(wrapper_name, key, secret, cur, coin, amount, price, dir):
    module = importlib.import_module('libs.{}'.format(wrapper_name))
    data = module.Private(key, secret).create_order(cur, coin, amount, price, dir)
    print(data)


if __name__ == "__main__":
    if len(sys.argv) == 2:
        test_wrapper_ticker(sys.argv[1])
    elif len(sys.argv) == 4:
        test_wrapper_balance(
            sys.argv[1], sys.argv[2], sys.argv[3]
            ) # wrapper, key, secret
    elif len(sys.argv) == 9:
        test_wraper_create_order(
            sys.argv[1], 
            sys.argv[2], 
            sys.argv[3], 
            sys.argv[4], 
            sys.argv[5], 
            sys.argv[6], 
            sys.argv[7], 
            sys.argv[8]
        ) # wrapper, key, secret, cur, coin, amount, price, dir
    else:
        test_all_wrappers()
