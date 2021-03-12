import hmac, time
from libs import Request

from urllib.parse import urlencode
import logging

base_url = "https://btcpop.co"


class Normalizer(object):
    """
        Normalize data.

        :param raw_data
            Data to be normalized. 
    """
    def __init__(self, raw_data):
        self.raw_data = raw_data

    def normalize_symbols(self):
        """Normalize symbols data."""
        pass

    def normalize_ticker(self):
        """Normalize tickers data."""
        return {
        "cur": "BTC",
        "coin": self.raw_data["ticker"],
        "last_price": self.raw_data["lastTradePrice"] \
            if isinstance(self.raw_data["lastTradePrice"], float) else 0.0,
        "buy": self.raw_data["buyPrice"] ,
        "buy_amount": 0.0,
        "sell": self.raw_data["sellPrice"],
        "sell_amount": 0.0,
        "high": 0.0,
        "low": 0.0,
        "platform": "btcpop"
    }

    def normalize_balances(self):
        """Normalize balances data."""
        pass


class Public(object):
    """Public endpoints."""

    @classmethod
    def get_tickers(cls):
        """Fetch tickers from echange"""
        suffix = "/api/market-public.php"
        req = Request(base_url, suffix)
        data = req.get()
        if data is not None:
            for i in data:
                parser = Normalizer(i)
                rsl = parser.normalize_ticker()
                if not rsl == None:
                    yield rsl


class Private(object):
    """
        Private endpoints.

        :param key
            API key to be used.
        :param secret
            API secret to be used.
    """
    def __init__(self, key, secret):
        self.key = key
        self.secret = secret

    def create_signature(self, secret, suffix):
        pass

    def get_balances(self):
        """Get Balances from exchange"""
        pass


    def create_order(self, cur, coin, amount, price, dir):
        """
            Create a trade order.
            In bitfinex direction is indicated by amount being positive or negative.

            :param cur
                Currency to user to create the trade order.
            :param coin
                Coin to use to create the trade order.
            :param amount
                Amount to be used to create the order. If the direction equal "buy"
                amount is positive, else if direction equals "sell"
                amount is negative or multiplied by -1.
            :param price
                Price to use to create the trade order.
            :param dir
                Unused paramenter, kept for compatibility.
        """
        pass



def create_order(key, secret, cur, coin, amount, price, dir):
    return Private(key,secret).create_order(cur, coin, amount, price, dir)
    
   
def get_balances(key, secret):
    return Private(key, secret).get_balances()


def get_tickers():
    return Public.get_tickers()

def run():
    #for backwards compatibility
    return Public.get_tickers()