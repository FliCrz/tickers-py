import hmac, time, base64
from libs import Request

from urllib.parse import urlencode
import logging


# api docs https://www.okex.com/docs/en/


base_url = "https://www.okex.com"


# only spot account supported

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
            "cur": self.raw_data["product_id"].split("-")[1],
            "coin": self.raw_data["product_id"].split("-")[0],
            "last_price": self.raw_data["last"],
            "buy": self.raw_data["best_bid"],
            "buy_amount": self.raw_data["best_bid_size"],
            "sell": self.raw_data["best_ask"],
            "sell_amount": self.raw_data["best_ask_size"],
            "high": self.raw_data["high_24h"],
            "low": self.raw_data["low_24h"],
            "platform": "okex"
        }

    def normalize_balances(self):
        """Normalize balances data."""
        balances = []
        for entry in self.raw_data:
            balances.append({
                "coin": entry["currency"],
                "balance": entry["balance"]
            })
        return balances


class Public(object):
    """Public endpoints."""

    @classmethod
    def get_tickers(cls):
        """Fetch tickers from echange"""
        suffix = "/api/spot/v3/instruments/ticker"
        req = Request(base_url, suffix)
        data = req.get()
        for i in data:
            parser = Normalizer(i)
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

    def create_signature_headers(self, suffix, **params):
        timesamp = int(time.time() * 1000)
        sign_string = timestamp + "GET" + suffix
        if params:
            sign_string += urllib.urlencode(params)
        signature = base64.b64encode(
            hmac.new(
                self.secret.encode("utf-8"),
                sign_string.encode("utf-8"),
                digestmod="SHA256"
                ).hexdigest()).decode()
        headers = {
            "OK-ACCESS-KEY": self.key,
            "OK-ACCESS-SIGN": signature,
            "OK-ACCESS-TIMESTAMP": str(timestamp),
            "OK-ACCESS-PASSPHRASE": "arbator"
        }
        return headers

    def get_balances(self):
        """Get Balances from exchange"""
        suffix = "api/spot/v3/accounts",
        headers = self.create_signature_headers(suffix)
        req = Request(base_url, suffix)
        rsl = req.get()
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
        suffix = "/api/spot/v3/orders"
        data = {
            "type": "limit",
            "side": dir,
            "instrument_id": "{}-{}".format(coin, cur),
            "size": amount,
            "price": price,
            "order_type": 3
        }
        headers = self.create_signature_headers(suffix, data)
        req = Request(base_url, suffix)
        rsl = req.post(headers, data)
        if rsl["result"] == True:
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