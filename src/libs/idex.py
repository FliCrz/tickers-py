import hmac, time
from libs import Request

from urllib.parse import urlencode
import logging


# api docs https://docs.idex.market/

base_url = "https://api.idex.market"


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
        k = self.raw_data["symbol"]
        vals = self.raw_data["data"]
        book = Public.get_book(k)
        if book:
            buy_amount = book["bids"][0]["amount"] if len(book["bids"]) > 0 else 0
            sell_amount = book["asks"][0]["amount"] if len(book["asks"]) > 0 else 0
        else:
            buy_amount = 0
            sell_amount = 0
        return {
            "cur": str(k.split("_")[0]).upper(),
            "coin": str(k.split("_")[1]).upper(),
            "last_price": vals["last"] if isinstance(vals["last"], float) else 0.0,
            "buy": vals["highestBid"] if isinstance(vals["highestBid"], float) else 0.0,
            "buy_amount":  buy_amount,
            "sell": vals["lowestAsk"] if isinstance(vals["lowestAsk"], float) else 0.0,
            "sell_amount": sell_amount,
            "high": vals["high"] if isinstance(vals["high"], float) else 0.0,
            "low": vals["low"] if isinstance(vals["low"], float) else 0.0,
            "platform": "idex"
        }


    def normalize_balances(self):
        """Normalize balances data."""
        balances = []
        for i in self.raw_data:
            balances.append({
                "coin": i,
                "balance": self.raw_data[i]["available"] + self.raw_data[i]["onOrders"]
            })
        return balances


class Public(object):
    """Public endpoints."""

    @classmethod
    def get_book(cls, symbol):
        endpoint = "/returnOrderBook"
        data = {
            "market": symbol,
            "count": 1
        }
        req = Request(base_url, endpoint)
        rsl = req.post(None, data)
        return rsl

    @classmethod
    def get_tickers(cls):
        """Fetch tickers from echange"""
        endpoint = "/returnTicker"
        req = Request(base_url, endpoint)
        rsl = req.get()
        for i in rsl:
            if i != None:
                parser = Normalizer({"symbol": i, "data": rsl[i]})
                yield parser.normalize_ticker()


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

    def get_balances(self):
        """Get Balances from exchange"""
        endpoint = "/returnCompleteBalances"
        req = Request(base_url, endpoint)
        rsl = req.post(None, {"address": self.key})
        return Normalizer(rsl).normalize_balances()

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