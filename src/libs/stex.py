import hmac, time
from libs import Request

from urllib.parse import urlencode


# api docs https://apidocs.stex.com/


base_url = "https://api3.stex.com"


##
#
# TODO private endpoints with OAUTH2.0
#
##


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
        buy_amount = self.raw_data["book"]["bid"][0]["amount"] if len(
            self.raw_data["book"]["bid"]
        ) > 0 else 0
        sell_amount = self.raw_data["book"]["ask"][0]["amount"] if len(
            self.raw_data["book"]["ask"]
        ) > 0 else 0
        return {
            "cur": self.raw_data["market_code"].upper(),
            "coin": self.raw_data["currency_code"].upper(),
            "last_price": self.raw_data["last"],
            "buy": self.raw_data["bid"],
            "buy_amount": buy_amount,
            "sell": self.raw_data["ask"],
            "sell_amount": sell_amount,
            "high": self.raw_data["high"],
            "low": self.raw_data["low"],
            "platform": "stex"
        }
        
    def normalize_balances(self):
        """Normalize balances data."""
        pass


class Public(object):
    """Public endpoints."""

    @classmethod
    def get_book(cls, symbol):
        endpoint = "/public/orderbook/{}".format(symbol)
        req = Request(base_url, endpoint)
        rsl = req.get()
        return rsl

    @classmethod
    def get_symbols(cls):
        endpoint = "/public/currency_pairs/list/ALL"
        req = Request(base_url, endpoint)
        rsl = req.get()
        return rsl["data"]

    @classmethod
    def get_tickers(cls):
        """Fetch tickers from echange"""
        endpoint = "/public/ticker"
        req = Request(base_url, endpoint)
        rsl = req.get()
        markets = cls.get_symbols()
        if rsl != None:
            for i in rsl["data"]:
                for m in markets:
                    if i["currency_code"] == m["currency_code"] and \
                        i["market_code"] == m["market_code"]:
                        book = cls.get_book(m["id"])
                        if book != None:
                            i["book"] = book["data"]
                            parser = Normalizer(i)
                            parsed = parser.normalize_ticker()
                            if not parsed == None:
                                yield parsed


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