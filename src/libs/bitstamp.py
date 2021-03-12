import time, hmac
from libs import Request

from urllib.parse import urlencode
from uuid import uuid4
import logging


# api docs https://www.bitstamp.net/api/

base_url = "https://www.bitstamp.net"


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
        book = Public().get_book(self.raw_data["symbol"])
        buy_amount =  book["bids"][0][1] if len(book["bids"]) > 0 else 0
        sell_amount = book["asks"][0][1] if len(book["asks"]) > 0 else 0
        return {
            "cur": self.raw_data["symbol"][3:].upper(),
            "coin": self.raw_data["symbol"][:3].upper(),
            "last_price": self.raw_data["data"]["last"],
            "buy": self.raw_data["data"]["bid"],
            "buy_amount": buy_amount,
            "sell": self.raw_data["data"]["ask"],
            "sell_amount": sell_amount,
            "high": self.raw_data["data"]["high"],
            "low": self.raw_data["data"]["low"],
            "platform": "bitstamp"
        }
        
    def normalize_balances(self):
        """Normalize balances data."""
        pass


class Public(object):
    """Public endpoints."""

    @classmethod
    def get_symbols(cls):
        """Dummy function for compatibility."""
        return [
            "btcusd", 
            "btceur", 
            "eurusd", 
            "xrpusd", 
            "xrpeur", 
            "xrpbtc", 
            "ltcusd", 
            "ltceur", 
            "ltcbtc", 
            "ethusd", 
            "etheur", 
            "ethbtc", 
            "bchusd", 
            "bcheur", 
            "bchbtc"
        ]

    @classmethod
    def get_book(cls, pair):
        """Get order book from exchange."""
        endpoint = "/api/order_book/{}".format(pair)
        for pair in cls.get_symbols():
            req = Request(base_url, endpoint)
            rsl = req.get()
            return rsl

    @classmethod
    def get_tickers(cls):
        """Fetch tickers from echange"""
        endpoint = "/api/ticker/"
        pair_list = cls.get_symbols()
        for pair in pair_list:
            req = Request(base_url, "{}{}".format(endpoint, pair))
            rsl = req.get()
            if not rsl == None:
                parser = Normalizer({"symbol": pair, "data":rsl})
                normalized =  parser.normalize_ticker()
                yield normalized


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

    def create_signature_headers(self, endpoint, payload):
        auth_header = "BITSTAMP " + self.key
        nonce = str(uuid4())
        timestamp = str(int(time.time() * 1000))
        message = auth_header + \
            "POST" + \
            "www.bitstamp.net" + \
            endpoint + \
            "" + \
            nonce + \
            timestamp + \
            "v2" + \
            urlencode(payload)
        signature = hmac.new(
            bytearray(self.secret, "utf-8"),
            message.encode("utf-8"), 
            digestmod="SHA256"
            ).hexdigest()
        headers = {
            "X-Auth": auth_header,
            "X-Auth-Signature": signature,
            "X-Auth-Nonce": nonce,
            "X-Auth-Timestamp": timestamp,
            "X-Auth-Version": "v2"
        }
        return headers

    def get_balances(self):
        """Get Balances from exchange"""
        endpoint = "/api/v2/balance/"
        headers = create_signature_headers(endpoint, "")
        req = Request(base_url, endpoint)
        rsl = req.post(headers)
        balances = []
        for entry in rsl:
            if "balance" in entry.split("_")[1]:
                balances.append({
                    "coin": entry.split("_")[0].upper(),
                    "balance": rsl[entry]
                })
        return balances

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
        endpoint = "/api/{}/{}_{}".format(dir, cur, coin)
        payload = {
            "amount": amount,
            "price": price,
            "ioc_order": True
        }
        headers = self.create_signature_headers(endpoint, payload)
        req = Request(base_url, endpoint)
        rsl = req.post(headers, payload)
        if "error" in rsl.keys():
            logging.error(rsl)
        logging.info(rsl)
        return rsl



def create_order(key, secret, cur, coin, amount, price, dir):
    return Private(key,secret).create_order(cur, coin, amount, price, dir)
    
   
def get_balances(key, secret):
    return Private(key, secret).get_balances()


def get_tickers():
    return Public().get_tickers()

def run():
    #for backwards compatibility
    return Public().get_tickers()