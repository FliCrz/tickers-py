import hmac, time, base64
from libs import Request

from urllib.parse import urlencode
import logging

# api docs https://huobiapi.github.io/docs/spot/v1/en/#introduction

base_url = "https://api.huobi.pro"


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
        if len(self.raw_data["symbol"]) % 2 == 0:
            cur = self.raw_data["symbol"][int(len(self.raw_data["symbol"]) / 2):].upper()
            coin = self.raw_data["symbol"][:int(len(self.raw_data["symbol"]) / 2)].upper()
            return {
                "cur": cur,
                "coin": coin,
                "last_price": (self.raw_data["bid"] + self.raw_data["ask"]) / 2,
                "buy": self.raw_data["bid"],
                "buy_amount": self.raw_data["bidSize"],
                "sell": self.raw_data["ask"],
                "sell_amount": self.raw_data["askSize"],
                "high": self.raw_data["high"],
                "low": self.raw_data["low"],
                "platform": "huobi"
            }

    def normalize_balances(self):
        """Normalize balances data."""
        balances = []
        for i in self.raw_data:
            balances.append({
                "coin": i["currency"],
                "symbol": i["balance"]
            })
        return balances


class Public(object):
    """Public endpoints."""

    @classmethod
    def get_tickers(cls):
        """Fetch tickers from echange"""
        suffix_ticker = "/market/tickers"
        req = Request(base_url, suffix_ticker)
        data = req.get()["data"]
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

    def create_signature(self, query_str):
        signature = hmac.new(
                bytearray(self.secret, "utf-8"),
                query_str.encode("utf-8"),
                digestmod="SHA256"
            ).hexdigest()
        return base64.b64encode(bytearray(signature, "utf-8")).decode()

    def get_balances(self):
        """Get Balances from exchange"""
        # FIXME {"err-code": "api-signature-not-valid", "err-msg": "Signature not valid: Verification failure [校验失败]", "data": None, "status": "error"}
        # https://huobiapi.github.io/docs/spot/v1/en/#authentication
        # https://huobiapi.github.io/docs/spot/v1/en/#get-the-aggregated-balance-of-all-sub-users
        suffix = "/v1/subuser/aggregate-balance"
        timestamp = urllib.parse.quote(datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S"))
        query_str = \
            "AccessKeyId={}&SignatureMethod=HmacSHA256&SignatureVersion=2&Timestamp={}".format(
                key, timestamp
            )
        message = "GET\napi.huobi.pro\n{}\n{}".format(suffix, query_str)
        # print(message)
        signature = self.create_signature(message)
        endpoint = suffix + "?" + query_str + "&Signature=" +  urllib.parse.quote(signature)
        req = Request(base_url, endpoint)
        rsl = req.get()
        parser = Normalizer(rsl["data"])
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
        suffix = "/v1/order/orders/place"
        # TODO buy/sell methods
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