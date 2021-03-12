import hmac, time
from libs import Request

from urllib.parse import urlencode
import logging

# api docs https://docs.poloniex.com/#introduction

base_url = "https://poloniex.com"


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
        key = self.raw_data["symbol"]
        values = self.raw_data["data"]
        return {
            "cur": key.split("_")[0].upper(),
            "coin": key.split("_")[1].upper(),
            "last_price": values["last"],
            "buy": values["highestBid"],
            "buy_amount": values["book"]["bids"][0][1] if len(values["book"]["bids"]) > 0 else 0,
            "sell": values["lowestAsk"],
            "sell_amount": values["book"]["asks"][0][1] if len(values["book"]["asks"]) > 0 else 0,
            "high": values["high24hr"],
            "low": values["low24hr"],
            "platform": "poloniex"
        }

    def normalize_balances(self):
        """Normalize balances data."""
        balances = []
        for i in self.raw_data:
            balances.append({
                "coin": i,
                "balance": rsl[i]["available"] + rsl[i]["onOrders"]
            })
        return balances


class Public(object):
    """Public endpoints."""

    @classmethod
    def get_book(cls):
        suffix = "/public?command=returnOrderBook&currencyPair=all&depth=1"
        req = Request(base_url, suffix)
        rsl = req.get()
        return rsl

    @classmethod
    def get_tickers(cls):
        """Fetch tickers from exchange"""
        suffix = "/public?command=returnTicker"
        req = Request(base_url, suffix)
        data = req.get()
        book = cls.get_book()
        for i in data:
            for b in book:
                if i == b:
                    data[i]["book"] = book[b]
                    parser = Normalizer({"symbol": i, "data": data[i]})
                    rsl =  parser.normalize_ticker()
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

    def create_signature_headers(self, data):
        signature = hmac.new(
            self.secret.encode("utf-8"),
            data.encode("utf-8"),
            digestmod="SHA512"
        ).hexdigest()
        headers = {
            "Key": self.key,
            "Sign": signature
        }
        return headers

    def get_balances(self):
        """Get Balances from exchange"""
        suffix = "/tradingApi?"
        data = "command=returnCompleteBalances&nonce={}".format(
            int(time.time() * 1000)
        )
        headers = self.create_signature_headers(data)
        req = Request(base_url, suffix)
        rsl = req.post(headers, data)
        parser = Normalizer(rsl)
        return parser.normalize_balances()

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
        suffix = "/tradingApi?"
        data = {
            command: dir,
            currencyPair: "{}_{}".format(cur, coin),
            rate: price,
            amount: amount,
            immediateOrCancel: 1
        }
        headers = self.create_signature_headers(data)
        req = Request(base_url, suffix)
        rsl = req.post(headers, data)
        if "orderNumber" in rsl.keys():
            return True
        return False



def create_order(key, secret, cur, coin, amount, price, dir):
    return Private(key,secret).create_order(cur, coin, amount, price, dir)
    
   
def get_balances(key, secret):
    return Private(key, secret).get_balances()


def get_tickers():
    return Public.get_tickers()

def run():
    #for backwards compatibility
    return Public.get_tickers()