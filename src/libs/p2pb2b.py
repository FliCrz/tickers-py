import hmac, time, base64
from libs import Request

from urllib.parse import urlencode
import logging

# api docs https://documenter.getpostman.com/view/6288660/SVYxnEmD?version=latest   

base_url = "https://api.p2pb2b.io"


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
        symbol = self.raw_data["symbol"]
        values = self.raw_data["data"]

        buy_book = Public.get_book(symbol, "buy")
        if buy_book:
            buy_amount = buy_book["result"]["orders"][0]["amount"] if len(
                buy_book["result"]["orders"]
            ) > 0 else 0
        else: buy_amount = 0
        sell_book = Public.get_book(symbol, "sell")
        if sell_book:
            sell_amount = sell_book["result"]["orders"][0]["amount"] if len(
                sell_book["result"]["orders"]
            ) > 0 else 0
        else: sell_amount =0

        return {
            "cur": str(symbol.split("_")[1]).upper(),
            "coin": str(symbol.split("_")[0]).upper(),
            "last_price": values["ticker"]["last"],
            "buy": values["ticker"]["bid"],
            "buy_amount": buy_amount,
            "sell": values["ticker"]["ask"],
            "sell_amount": sell_amount,
            "high": values["ticker"]["high"],
            "low": values["ticker"]["low"],
            "platform": "p2pb2b"
        }
        
        
    def normalize_balances(self):
        """Normalize balances data."""
        balances = []
        for i in self.raw_data:
            balances.append({
                "coin": i,
                "balance": self.raw_data[i]["available"] + self.raw_data[i]["freeze"]
            })
        return balances


class Public(object):
    """Public endpoints."""

    @classmethod
    def get_book(cls, symbol, dir):
        """
            Get book for target symbol.
            
            :param symbol
                Market symbol to get the book.
            :param dir
                Direction of the market to get the book.
        """        
        endpoint = "/api/v1/public/book?market={}&side={}&offset=0&limit=1".format(
            symbol, dir
        )
        req = Request(base_url, endpoint)
        rsl = req.get()
        return rsl

    @classmethod
    def get_tickers(cls):
        """Fetch tickers from echange"""
        endpoint = "/api/v1/public/tickers"
        req = Request(base_url, endpoint)
        rsl = req.get()
        for i in rsl["result"]:
            if i != None:
                parser = Normalizer({"symbol": i, "data": rsl["result"][i]})
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

    def create_signature_headers(self, body):
        """
            Create signature headers to add to the authenticated request.

            :param body
                Body of the request.
        """
        payload = base64.b64encode(
            urlencode(body)
        ).decode()
        signature = hmac.new(
            self.secret.encode("utf-8"),
            payload.encode("utf-8"),
            digestmod="SHA512"
        ).hexdigest()
        headers = {
            "Content-Type": "application/json",
            "X-TXC-APIKEY": self.key,
            "X-TXC-PAYLOAD": self.secret,
            "X-TXC-SIGNATURE": signature
        }
        return headers

    def get_balances(self):
        """Get Balances from exchange"""
        endpoint = "/api/v1/account/balances"
        body = {
            "request": endpoint,
            "nonce": str(int(time.time() * 1000))
        }
        headers = self.create_signature_headers(body)
        req = Request(base_url, endpoint)
        rsl = req.get(headers)
        rsp = requests.get(base_url + endpoint, headers=headers)
        return Normalizer(rsl["result"]).normalize_balances()

    def cancel_order(self, order_id, symbol):
        """
            Cancel given order.

            :param order_id
                Id of the order to be cancelled.
            :param symbol
                Market symbol where to cancel the order.
        """
        endpoint = "/api/v1/order/cancel"
        data = {
            "market": symbol,
            "orderId": order_id,
            "request": endpoint,
            "nonce": str(int(time.time() * 1000))
        }
        headers = self.create_signature_headers(data)
        req = Request(base_url, endpoint)
        rsl = req.post(headers, data)
        if rsl["success"] == False:
            logging.error("Error canceling order {} in {}".format(
                rsl, __name__.upper()
            ))
        return rsl

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
        endpoint = "/api/v1/order/new"
        symbol = "{}_{}".format(coin, cur)
        data = {
            "market": symbol,
            "side": dir,
            "amount": amount,
            "price": price,
            "request": endpoint,
            "nonce": str(int(time.time() * 1000))
        }
        headers = self.create_signature_headers(data)
        req = Request(base_url, endpoint)
        rsl = req.post(headers, data)
        if rsl["success"] == True:
            order_id = rsl["result"]["orderId"]
            time.sleep(5)
            if self.cancel_order(order_id, symbol):
                return True
        logging.error("Error canceling order {} in {}".format(
                rsl, __name__.upper()
            ))
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