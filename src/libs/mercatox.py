import hmac, time, base64, json
from libs import Request

from urllib.parse import urlencode
import logging


base_url = "https://mercatox.com"


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
        v = self.raw_data["data"]

        buy_amount, sell_amount = 0, 0

        book = Public().get_book(k)
        if book:
            if "bids" in book.keys():
                if book["bids"] != None:
                    buy_amount = book["bids"][0][1] if len(book["bids"]) > 0 else 0
            if "asks" in book.keys():
                if book["asks"] != None:
                    sell_amount = book["asks"][0][1] if len(book["asks"]) > 0 else 0 
        return {
            "cur": k.split("_")[1].upper(),
            "coin": k.split("_")[0].upper(),
            "last_price": v["last_price"],
            "buy": v["highestBid"],
            "buy_amount": buy_amount,
            "sell": v["lowestAsk"],
            "sell_amount": sell_amount,
            "high": v["high24hr"],
            "low": v["low24hr"],
            "platform": "mercatox"
        }
            

    def normalize_balances(self):
        """Normalize balances data."""
        pass


class Public(object):
    """Public endpoints."""

    @classmethod
    def create_sign_string(cls, data):
        """
            Create a signed string from data.

            :param data
                Data to be encrypted/signed.
        """
        return base64.b64encode(
            json.dumps(data).encode(utf-8)
            ).decode()

    @classmethod
    def get_book(cls, symbol):
        """
            Get book from exchange for symbol.

            :param symbol
                Symbol to be used for the request.
        """
        endpoint = "/api/public/v1/orderbook?market_pair={}".format(symbol)
        req = Request(base_url, endpoint)
        return req.get()

    @classmethod
    def get_tickers(cls):
        """Fetch tickers from echange"""
        endpoint = "/api/public/v1/ticker"
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

    def create_signature(self, data):
        """
            Create signature from data with api secret.

            :param data
                Data to be used for the signature.
        """
        return base64.b64encode(
            hamc.new(
            self.secret.encode("utf-8"),
            Public.create_sign_string(data).encode("utf-8"),
            digestmod="SHA1"
        )).decode()

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