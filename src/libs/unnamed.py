import hmac, time
from libs import Request

from urllib.parse import urlencode
import logging


# api docs https://www.unnamed.exchange/Home/Api

base_url = "https://api.unnamed.exchange"


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
        book = Public().get_book(self.raw_data["market"])
        return {
            "cur": self.raw_data["market"].split("_")[1],
            "coin": self.raw_data["market"].split("_")[0],
            "last_price": 0,
            "buy": float(self.raw_data["highestBuy"]),
            "buy_amount": book["buy"][0]["amount"] if len(book["buy"]) > 0 else 0 ,
            "sell": float(self.raw_data["lowestSell"]),
            "sell_amount": book["sell"][0]["amount"] if len(book["sell"]) > 0 else 0,
            "high": float(self.raw_data["high"]),
            "low": float(self.raw_data["low"]),
            "platform": "unnamed"
        }

    def normalize_balances(self):
        """Normalize balances data."""
        balances = []
        for i in self.raw_data:
            balances.append({
                "coin": i["symbol"],
                "balance": i["total"]
            })
        return balances


class Public(object):
    """Public endpoints."""

    @classmethod
    def get_book(cls, pair):
        suffix = "/v1/Public/OrderBook?market={}&depth=1".format(pair)
        req = Request(base_url, suffix)
        return req.get()

    @classmethod
    def get_tickers(cls):
        """Fetch tickers from echange"""
        suffix = "/v1/Public/Ticker"
        req = Request(base_url, suffix)
        data = req.get()
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

    def create_signature_headers(self, data):
        signature = hmac.new(
            self.secret.encode("utf-8"),
            data.encode("utf-8"),
            digestmod="SHA512"
        ).hexdigest()
        headers = {
            "ApiKey": self.key,
            "Signature": Signature
        }
        return headers

    def get_balances(self):
        """Get Balances from exchange"""
        suffix = "/v1/Trade/BalanceFull"
        nonce = str(int(time.time() * 1000))
        headers = self.create_signature_headers({"nonce": nonce})
        req = Request(base_url, suffix)
        rsl = req.get(headers=headers)
        parser = Normalizer(rsl)
        return parser.normalize_balances()


    def cancel_order(order_id):
        suffix = "/v1/Trade/OrderCancel"
        nonce = str(int(time.time() * 1000))
        data = {
            "nonce": nonce,
            "market": "{}_{}".format(coin, cur),
            "cancelType": "Trade",
            "orderId": order_id
        }
        headers = self.create_signature_headers({"data": data})
        req = Request(base_url, endpoint)
        rsl = req.post(headers, data)
        if "error" in rsl.keys():
            return False
        return True


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
        suffix = "/v1/Trade/OrderSubmit"    
        nonce = str(int(time.time() * 1000))
        data = {
            "nonce": nonce,
            "market": "{}_{}".format(coin, cur),
            "orderType": "Limit",
            "type": dir,
            "amount": amount,
            "price": price,
        }
        headers = self.create_signature_headers({"data": data})
        req = Request(base_url, suffix)
        rsl = req.post(headers, data)
        order_id = rsl["orderId"]
        if not order_id: return False
        return self.cancel_order(order_id)



def create_order(key, secret, cur, coin, amount, price, dir):
    return Private(key,secret).create_order(cur, coin, amount, price, dir)
    
   
def get_balances(key, secret):
    return Private(key, secret).get_balances()


def get_tickers():
    return Public.get_tickers()

def run():
    #for backwards compatibility
    return Public.get_tickers()