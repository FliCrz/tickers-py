import hmac, time
from libs import Request

from urllib.parse import urlencode
import logging

# api docs https://github.com/coinexcom/coinex_exchange_api/wiki/

base_url = "https://api.coinex.com"



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
        currency_list = ["BTC", "BCH", "ETH", "CET", "USDT"]
        cur =  self.raw_data["symbol"][int(len(self.raw_data["symbol"]) / 2):]
        coin = self.raw_data["symbol"][:int(len(self.raw_data["symbol"]) / 2)]
        if cur in currency_list: 
            return  {
                "cur": cur,
                "coin": coin,
                "last_price": self.raw_data["data"]["last"],
                "buy": self.raw_data["data"]["buy"],
                "buy_amount": self.raw_data["data"]["buy_amount"],
                "sell": self.raw_data["data"]["sell"],
                "sell_amount": self.raw_data["data"]["sell_amount"],
                "high": self.raw_data["data"]["high"],
                "low": self.raw_data["data"]["low"],
                "platform": "coinex"
            }

    def normalize_balances(self):
        """Normalize balances data."""
        balances = []
        for i in self.raw_data:
            balances.append({
                "coin":i.upper(),
                "balance": (
                  self.raw_data[i]["available"] + self.raw_data["i"]["frozen"]
                )
            })
        return balances


class Public(object):
    """Public endpoints."""

    @classmethod
    def get_tickers(cls):
        """Fetch tickers from echange"""
        suffix = "/v1/market/ticker/all"
        req = Request(base_url, suffix)
        rsl = req.get()
        data = rsl["data"]["ticker"]
        if data is not None:
            for i in data:
                if len(i) <= 10:
                    parser = Normalizer({"symbol":i, "data":data[i]})
                    entry = parser.normalize_ticker()
                    if not entry == None:
                        yield entry


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

    def create_signature_headers(self, query_str):
        # FIXME {"data": {}, "code": 25, "message": "Signature error."}
        # https://github.com/coinexcom/coinex_exchange_api/wiki/060balance
        # https://github.com/coinexcom/coinex_exchange_api/wiki/012security_authorization
        message = "{}&secret_key={}".format(query_str, self.secret)
        signature = hmac.new(
            bytearray(self.secret, "utf-8"),
            message.encode("utf-8"),
            digestmod="MD5"
        ).hexdigest().upper()
        return {
            "authorization": signature,
            "Content-Type":"application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36"
        }

    def get_balances(self):
        """Get Balances from exchange"""
        suffix = "/v1/balance/info?"
        nonce = str(int(time.time() * 1000))
        query_str = "access_id={}&tonce={}".format(self.key, nonce)
        headers = self.create_signature_headers(query_str)
        req = Request(base_url, suffix + query_str)
        rsl = req.get(headers=headers)
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
        suffix = "/v1/order/ioc?"
        nonce = str(int(time.time() * 1000))
        payload = {
            "access_id": self.key,
            "tonce": nonce,
            "market": cur + coin,
            "type": dir,
            "amount": amount,
            "price": price
        }
        query_str = urlencode(payload)
        headers = self.create_signature_headers(query_str)
        req = Request(base_url, suffix + query_str)
        rsl = req.post(headers, payload)
        if rsl["message"] == "ok":
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