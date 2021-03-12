import hmac, time
from libs import Request

from urllib.parse import urlencode
import logging

# api docs https://bittrex.github.io/api/v1-1

base_url = "https://api.bittrex.com"


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
        book = Public().get_book(self.raw_data["MarketName"])
        buy_amount =  book["buy"][0]["Quantity"] \
            if len(book["buy"]) > 0 else 0
        sell_amount = book["sell"][0]["Quantity"] \
            if len(book["sell"]) > 0 else 0
        return {
            "cur": self.raw_data["MarketName"].split("-")[0],
            "coin": self.raw_data["MarketName"].split("-")[1],
            "last_price": self.raw_data["Last"],
            "buy": self.raw_data["Bid"],
            "buy_amount": buy_amount,
            "sell": self.raw_data["Ask"],
            "sell_amount": sell_amount,
            "high": self.raw_data["High"],
            "low": self.raw_data["Low"],
            "platform": "bittrex"
        }

    def normalize_balances(self):
        """Normalize balances data."""
        balances = []
        for i in self.raw_data:
            balances.append({
                    "coin": i["Currency"].upper(),
                    "balance": i["Balance"]
                })
        return balances


class Public(object):
    """Public endpoints."""

    @classmethod
    def get_book(cls, pair):
        suffix = "/api/v1.1/public/getorderbook?market={}&type=both".format(pair)
        req = Request(base_url, suffix)
        data = req.get()
        return data["result"]

    @classmethod
    def get_tickers(cls):
        """Fetch tickers from echange"""
        endpoint = "/api/v1.1/public/getmarketsummaries"
        req = Request(base_url, endpoint)
        data = req.get()
        if data is not None:
            for i in data["result"]:
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

    def create_signature(self, suffix):
        message = base_url + suffix
        signature = hmac.new(
            bytearray(self.secret, "utf-8"), 
            message.encode("utf-8"), 
            digestmod="SHA512"
            ).hexdigest()
        return signature

    def get_balances(self):
        """Get Balances from exchange"""
        nonce = str(int(time.time() * 1000))
        suffix = "/api/v1.1/account/getbalances?apikey={}&nonce={}".format(self.key, nonce)
        headers = {
            "APISIGN": self.create_signature(suffix)
        }
        req = Request(base_url, suffix)
        rsl = req.get(headers=headers)
        parser = Normalizer(rsl["result"])
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
        prefix = "/api/v1.1/market"
        suffix = "/{}limit?apikey={}&market={}-{}&quantity={}&rate={}&timeInForce=IOC".format(
            dir, key, cur, coin, amount, price
        )
        endpoint = prefix + suffix
        headers = {
            "APISIGN": self.create_signature(endpoint)
        }
        req = Request(base_url, suffix)
        rsl = req.get(headers=headers)
        if rsl["success"] == "false":
            return False
        return True



def create_order(key, secret, cur, coin, amount, price, dir):
    return Private(key,secret).create_order(cur, coin, amount, price, dir)
    
   
def get_balances(key, secret):
    return Private(key, secret).get_balances()


def get_tickers():
    return Public.get_tickers()

def run():
    #for backwards compatibility
    return Public.get_tickers()