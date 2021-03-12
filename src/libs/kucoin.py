import hmac, time, base64
from libs import Request

from urllib.parse import urlencode
import logging

# api docs https://docs.kucoin.com/#getting-started

base_url = " https://api.kucoin.com"

#####
# TODO add following alert to frontend
# ATTENTION: due to kucoin particularity,
# API-PASSPHRASE must be set to: 
# arbator
#####


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
        book = Public().get_book(self.raw_data["symbol"])["data"]
        return {
            "cur": self.raw_data["symbol"].split("-")[1],
            "coin": self.raw_data["symbol"].split("-")[0],
            "last_price": self.raw_data["last"],
            "buy": self.raw_data["buy"],
            "buy_amount":  book["bestBidSize"],
            "sell": self.raw_data["sell"],
            "sell_amount": book["bestAskSize"],
            "high": self.raw_data["high"],
            "low": self.raw_data["low"],
            "platform": "kucoin"
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
    def get_book(cls, pair):
        endpoint = "/api/v1/market/orderbook/level1?symbol={}".format(pair)
        req = Request(base_url, endpoint)
        return req.get()

    @classmethod
    def get_tickers(cls):
        """Fetch tickers from echange"""
        endpoint = "/api/v1/market/allTickers"
        req = Request(base_url, endpoint)
        data = req.get()
        for i in data["data"]["ticker"]:
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

    def create_signature_headers(suffix):
        timestamp = str(int(time.time() * 1000))
        message = timestamp + "GET" + suffix
        signature = base64.b64encode(
            hmac.new(self.secret.encode("utf-8"), message.encode("utf-8"), digestmod="SHA256"
            ).hexdigest()).decode()
        headers = {
            "KC-API-KEY": key,
            "KC-API-SIGN": signature,
            "KC-API-TIMESTAMP": timestamp,
            "KC-API-PASSPHRASE": "arbator"
        }
        return headers

    def get_balances(self):
        """Get Balances from exchange"""
        suffix = "/api/v1/accounts"
        headers = self.create_signature_headers(suffix)
        req = Request(base_url, suffix)
        rsp = req.get(headers)
        parser = Normalizer(rsp["data"])
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
        suffix = "/api/v1/orders"
        headers = self.create_signature_headers(suffix)
        data = {
            "side": dir,
            "symbol": "{}-{}".format(coin, cur),
            "price": price,
            "size": amount,
            "timeInForce": "IOC"
        }
        req = Request(base_url, suffix)
        rsl = req.post(headers, data)
        if "orderId" in rsl.keys():
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