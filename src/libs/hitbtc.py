import hmac, time, requests
from libs import Request

from urllib.parse import urlencode
import logging

# api docs https://api.hitbtc.com/

base_url = "https://api.hitbtc.com"


class RequestWithSession(object):

    def __init__(self, base_url, endpoint, key, secret):
        self.counter = 1
        self.base_url = base_url
        self.endpoint = endpoint
        self.key = key
        self.secret = secret

    def get(self):
        session = requests.session()
        session.auth = (self.key, self.secret)
        rsp = session.get(base_url + suffix)
        if rsp.status_code == 200:
            return rsp.json()
        elif rsp.status_code > 500:
            logging.error(
                "ConnectionError: {} from {}. Waiting: {}".format(
                    rsp.text, 
                    url, 
                    int(self.counter * config.API_SERVER_NOT_AVAILABLE_TIMEOUT)
                ))
            time.sleep(config.API_SERVER_NOT_AVAILABLE_TIMEOUT * self.counter)
            self.counter = self.counter + 1
            self.get()
        else:
            logging.error(
                "ConnectionError: MaximumRequests from {}. Waiting: {}".format(
                    url, int(self.counter * config.API_SERVER_CALLS_TIMEOUT)
            ))
            time.sleep(config.API_SERVER_CALLS_TIMEOUT * self.counter)
            self.counter = self.counter + 1
            self.get()

    def post(self, data):
        session = requests.session()
        session.auth = (key, secret)
        rsp = session.post(base_url + suffix, data=data)
        return rsp.json()



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
            buy_amount =  self.raw_data["book"]["bid"][0]["size"] if len(
                self.raw_data["book"]["bid"]
            ) > 0 else 0
            sell_amount = self.raw_data["book"]["ask"][0]["size"] if len(
                self.raw_data["book"]["ask"]
            ) > 0 else 0
            return {
                "cur": self.raw_data["symbol"][int(
                    len(self.raw_data["symbol"]) / 2
                ):],
                "coin": self.raw_data["symbol"][:int(
                    len(self.raw_data["symbol"]) / 2
                )],
                "last_price": self.raw_data["last"],
                "buy": self.raw_data["bid"],
                "buy_amount": buy_amount, 
                "sell": self.raw_data["ask"],
                "sell_amount": sell_amount,
                "high": self.raw_data["high"],
                "low": self.raw_data["low"],
                "platform": "hitbtc"
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
    def get_book(cls):
        suffix ="/api/2/public/orderbook?limit=1"
        req = Request(base_url, suffix)
        return req.get()

    @classmethod
    def get_tickers(cls):
        """Fetch tickers from echange"""
        suffix = "/api/2/public/ticker"
        req = Request(base_url, suffix)
        data = req.get()
        if data != None:
            book = cls.get_book()
            for i in data:
                for b in book:
                    if i["symbol"] == b:
                        i["book"] = book[b]
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

    def get_balances(self):
        """Get Balances from exchange"""
        suffix = "/api/2/account/balance"
        req = RequestWithSession(base_url, suffix, self.key, self.secret)
        rsl = req.get()
        parser = Normalizer(rsl)
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
        suffix = "/api/2/order"
        data = {
            "symbol": cur + coin,
            "side": dir,
            "quantity": amount,
            "price": price,
            "timeInForce": "IOC"
        }
        req = RequestWithSession(base_url, suffix, self.key, self.secret)
        rsl = req.post(data)
        if "error" in rsl.keys():
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