import hmac, time
from libs import Request

from urllib.parse import urlencode
import logging


# api docs https://www.yobit.net/en/api/

base_url =  "https://yobit.net"


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
        pair_list = []
        for i in self.raw_data:
            pair_list.append(i)
        return pair_list

    def normalize_ticker(self):
        """Normalize tickers data.""" 
        k = self.raw_data["symbol"]
        data = self.raw_data["data"]
        book = Public.get_book(k)
        if book:
            if "bids" in book[k].keys():
                buy_amount = book[k]["bids"][0][1] if len(
                    book[k]["bids"]
                ) > 0 else 0 
            else: buy_amount = 0
            if "asks" in book[k].keys():
                sell_amount = book[k]["asks"][0][1] if len(
                    book[k]["asks"]
                ) > 0 else 0
            else: sell_amount = 0
        else:
            buy_amount, sell_amount = 0, 0

        return {
            "cur": k.split("_")[1].upper(),
            "coin": k.split("_")[0].upper(),
            "last_price": data["last"],
            "buy": data["buy"],
            "buy_amount":  buy_amount,
            "sell": data["sell"],
            "sell_amount": sell_amount,
            "high": data["high"],
            "low": data["low"],
            "platform": "yobit"
        }

    
    def normalize_balances(self):
        """Normalize balances data."""
        pass


class Public(object):
    """Public endpoints."""

    @classmethod
    def get_symbols(cls):
        """Get symbols available"""
        endpoint = "/api/3/info"
        req = Request(base_url, endpoint)
        if req != None:
            rsl = req.get()["pairs"]
            parser = Normalizer(rsl)
            return parser.normalize_symbols()

    @classmethod
    def get_book(cls, symbol):
        """
            Get book for symbol.

            :param symbol
                Symbol to get the book from.
        """
        endpoint = "/api/3/depth/{}?limit=1".format(symbol)
        req = Request(base_url, endpoint)
        rsl = req.get()
        return rsl


    @classmethod
    def get_tickers(cls):
        """Fetch tickers from echange"""
        endpoint = "/api/3/ticker/"  
        pair_list = cls.get_symbols()
        pair_list_string = ""
        counter = 0
        while len(pair_list) >= counter:
            pair_list_string = "-".join(pair_list[counter:int(counter + 20)])
            pair_list_string = pair_list_string[1:]
            req = Request(base_url, "{}{}?ignore_invalid=1".format(
                endpoint, pair_list_string
            ))
            rsl = req.get()
            for i in rsl:
                parser = Normalizer({"symbol":i, "data": rsl[i]})
                yield parser.normalize_ticker()
            counter += 20


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

    def get_balances(self):
        """Get Balances from exchange"""
        pass

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