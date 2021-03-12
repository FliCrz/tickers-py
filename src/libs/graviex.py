import hmac, time
from libs import Request

from urllib.parse import urlencode
import logging


# api docs https://graviex.net/documents/api_v3

base_url = "https://graviex.net"


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
        book = Public.get_book(self.raw_data["name"])
        if book:
            buy_amount =  book["bids"][0][1] \
                if len(book["bids"]) > 0 else 0
            sell_amount = book["asks"][0][1] \
                if len(book["asks"]) > 0 else 0
        else:
            buy_amount, sell_amount = 0, 0
        return {
            "cur": self.raw_data["name"].split("/")[1].upper(),
            "coin": self.raw_data["name"].split("/")[0].upper(),
            "last_price": self.raw_data["last"],
            "buy": self.raw_data["buy"],
            "buy_amount": buy_amount,
            "sell": self.raw_data["sell"],
            "sell_amount": sell_amount,
            "high": self.raw_data["high"],
            "low": self.raw_data["low"],
            "platform": "graviex"
        }
       

    def normalize_balances(self):
        """Normalize balances data."""
        balances = []
        for e in self.raw_data["accounts_filtered"]:
            balances.append({
                "coin": e["currency"].upper(),
                "balance": e["balance"]
            })
        return balances


class Public(object):
    """Public endpoints."""
    @classmethod
    def get_book(cls, symbol):
        endpoint = "/api/v3/depth.json?market={}&limit=1".format("".join(symbol.split("/")).lower())
        time.sleep(1)
        req = Request(base_url, endpoint)
        rsl = req.get()
        return rsl

    @classmethod
    def get_tickers(cls):
        """Fetch tickers from echange"""
        endpoint = "/api/v3/tickers.json"
        req = Request(base_url, endpoint)
        rsl = req.get()
        if rsl != None:
            for i in rsl:
                parser = Normalizer(rsl[i])
                parsed = parser.normalize_ticker()
                yield parsed
            pass


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

    def create_signature(self, req_type, endpoint, query):
        """
            Create signature to add to authenticated rquests.

            :param req_type
                HTTP request type
            :param endpoint
                Endpoint of the request.
            :param query
                Query string to add to the request.
        """
        message = "{}|{}|{}".format(
            req_type, endpoint, query
        )
        signature = hmac.new(
            bytearray(self.secret, "utf-8"),
            message.encode("utf-8"),
            digestmod="SHA256"
        ).hexdigest()
        return signature

    def get_balances(self):
        """Get Balances from exchange"""
        endpoint = "/api/v3/members/me.json?"
        nonce = str(int(time.time() * 1000))
        query = "access_key={}&tonce={}".format(
            self.key, nonce
        )
        query_signed = "{}&signature={}".format(
            query, self.create_signature("GET", endpoint, query)
        )
        req = Request(base_url, "{}{}".format(endpoint, query_signed))
        rsl = req.get()
        if rsl:
            return Normalizer(rsl).normalize_balances()
        else: return [rsl]

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
        endpoint = "/api/v3/orders.json?"
        nonce = str(int(time.time() * 1000))
        data = {
            "access_key": self.key,
            "tonce": nonce,
            "market": coin.lower() + cur.lower(),
            "price": price,
            "side": dir,
            "volume": amount,
            "order_type": "IOC"
        }
        query = urlencode(data)
        signature = self.create_signature("POST", endpoint, query)
        query_signed = "{}&signature={}".format(
            query, signature
        )
        data["signature"] = signature
        req = Request(base_url, endpoint)
        rsl = req.post(headers=None, data=data)
        if "error" in rsl.keys():
            logging.error("Error passing order in {}".format(
                __name__.upper()
            ))
        return rsl


def create_order(key, secret, cur, coin, amount, price, dir):
    return Private(key,secret).create_order(cur, coin, amount, price, dir)
    
   
def get_balances(key, secret):
    return Private(key, secret).get_balances()


def get_tickers():
    return Public.get_tickers()

def run():
    #for backwards compatibility
    return Public.get_tickers()