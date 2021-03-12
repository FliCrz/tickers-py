import hmac, time, base64
from libs import Request

from urllib.parse import urlencode
import logging


# api docs https://docs.crex24.com/trade-api/v2/

base_url = "https://api.crex24.com"


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
        book = Public().get_book(self.raw_data)
        return {
            "cur": self.raw_data["instrument"].split("-")[1],
            "coin": self.raw_data["instrument"].split("-")[0],
            "last_price": self.raw_data["last"],
            "buy": self.raw_data["bid"],
            "buy_amount": book["buyLevels"][0]["volume"] if len(book["buyLevels"]) > 0 else 0,
            "sell": self.raw_data["ask"],
            "sell_amount": book["sellLevels"][0]["volume"] if len(book["sellLevels"]) > 0 else 0,
            "high": self.raw_data["high"],
            "low": self.raw_data["low"],
            "platform": "crex24"
        }

    def normalize_balances(self):
        """Normalize balances data."""
        balances = []
        for entry in self.raw_data:
            balances.append({
                "coin": entry["currency"].upper(),
                "balance": entry["available"] + entry["reserved"] 
            })
        return balances


class Public(object):
    """Public endpoints."""

    @classmethod
    def get_book(cls, pair):
        suffix = "/v2/public/orderBook?instrument={}&limit=1".format(
          pair["instrument"]
          )
        req = Request(base_url, suffix)
        return req.get()

    @classmethod
    def get_tickers(cls):
        """Fetch tickers from echange"""
        suffix = "/v2/public/tickers"
        req = Request(base_url, suffix)
        data = req.get()
        if data is not None:
            for i in data:
                if not i is None:
                    parser = Normalizer(i)
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

    def create_signature_headers(self, suffix):
        nonce = str(int(time.time() * 1000))
        message = suffix + nonce
        hashed = hmac.new(
            base64.b64decode(self.secret),
            message.encode("utf-8"),
            digestmod="SHA512"
        )
        signature = base64.b64encode(hashed.digest()).decode()
        return {
            "X-CREX24-API-KEY": self.key,
            "X-CREX24-API-NONCE": nonce,
            "X-CREX24-API-SIGN": signature
        }

    def get_balances(self):
        """Get Balances from exchange"""
        suffix = "/v2/account/balance"
        headers = self.create_signature_headers(suffix)
        req = Request(base_url, suffix)
        rsl = req.get(headers=headers)
        parser = Normalizer(rsl)
        return parser.normalize_balances()

    def cancel_order(self, order_id):
        suffix = "/v2/trading/cancelOrdersById"
        payload = {
            "ids": [order_id]
        }
        headers = self.create_signature_headers(suffix)
        req = Request(base_url, suffix)
        rsl = req.get()
        if order_id in rsl:
            return True
        return False

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
        suffix = "/v2/trading/placeOrder"
        payload = {
            "instrument": "{}-{}".format(coin, cur),
            "side": dir,
            "volume": amount,
            "price": price
        }
        headers = self.create_signature_headers(suffix)
        req = Request(base_url, suffix)
        rsl = req.post(headers, payload)
        order_id = rsl["id"]
        time.sleep(10)
        cancelled = self.cancel_order(order_id)
        return cancelled



def create_order(key, secret, cur, coin, amount, price, dir):
    return Private(key,secret).create_order(cur, coin, amount, price, dir)
    
   
def get_balances(key, secret):
    return Private(key, secret).get_balances()


def get_tickers():
    return Public.get_tickers()

def run():
    #for backwards compatibility
    return Public.get_tickers()