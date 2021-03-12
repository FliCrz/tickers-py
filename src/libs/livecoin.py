import hmac, time
from libs import Request

from urllib.parse import urlencode
import logging

# api docs https://www.livecoin.net/api?lang=en

base_url = "https://api.livecoin.net"

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
        buy_amount = self.raw_data["book"]["bids"][0][1] if len(
            self.raw_data["book"]["bids"]
        ) > 0 else 0
        sell_amount = self.raw_data["book"]["asks"][0][1] if len(
            self.raw_data["book"]["asks"]
        ) > 0 else 0
        return {
            "cur": self.raw_data["symbol"].split("/")[1],
            "coin": self.raw_data["symbol"].split("/")[0],
            "last_price": self.raw_data["last"],
            "buy": self.raw_data["best_bid"],
            "buy_amount":  buy_amount,
            "sell": self.raw_data["best_ask"],
            "sell_amount": sell_amount,
            "high": self.raw_data["high"],
            "low": self.raw_data["low"],
            "platform": "livecoin"
        }

    def normalize_balances(self):
        """Normalize balances data."""
        balances = []
        for i in self.raw_data:
            if i["type"] == "total":
                balances.append({
                    "coin": i["currency"],
                    "balance": i["value"]
                })
        return balances


class Public(object):
    """Public endpoints."""

    @classmethod
    def get_book(cls):
        suffix = "/exchange/all/order_book?&groupByPrice=true&depth=1"
        req = Request(base_url, suffix)
        return req.get()

    @classmethod
    def get_tickers(cls):
        """Fetch tickers from echange"""
        endpoint = "/exchange/ticker"
        req = Request(base_url, endpoint)
        data = req.get()
        book = cls.get_book()
        if data != None:
            for i in data:
                for b in book:
                    if i["symbol"] == b:
                        i["book"] = book[b]
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

    def create_signature_headers(self, suffix, **params):
        message = ""
        if len(params) > 0:
            message = urllib.urlencode(**params)
        signature = hmac.new(
            self.secret.encode("utf-8"),
            message.encode("utf-8"),
            digestmod="SHA256"
        ).hexdigest().upper()
        headers = {
            "Api-key": self.key,
            "Sign": signature
        }
        return headers

    def get_balances(self):
        """Get Balances from exchange"""
        suffix = "/payment/balances"
        req = Request(base_url, suffix)
        headers = self.create_signature_headers(suffix)
        rsl = req.get(headers=headers)
        parser = Normalizer(rsl)
        return parser.normalize_balances

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
        suffix = "/exchange/{}limit".format(dir)
        data = {
            "currencyPair": "{}/{}".format(coin, cur),
            "price": price,
            "quantity": amount
        }
        req = Request(base_url, suffix)
        headers = self.create_signature_headers(suffix, data)
        rsl = req.post(headers, data)
        if rsl["success"] == True:
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