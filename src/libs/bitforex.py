import hmac, time
import logging
from libs import Request


# api docs https://github.com/githubdev2020/API_Doc_en/wiki

base_url = " https://api.bitforex.com"


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
        book = Public.get_book(self.raw_data["symbol"])
        buy_amount =  book["bids"][0]["amount"] if len(book["bids"]) > 0 else 0
        sell_amount = book["asks"][0]["amount"] if len(book["asks"]) > 0 else 0
        return {
            "cur": self.raw_data["symbol"].split("-")[1].upper(),
            "coin": self.raw_data["symbol"].split("-")[2].upper(),
            "last_price": self.raw_data["data"]["last"],
            "buy": self.raw_data["data"]["buy"],
            "buy_amount": buy_amount,
            "sell": self.raw_data["data"]["sell"],
            "sell_amount": sell_amount,
            "high": self.raw_data["data"]["high"],
            "low": self.raw_data["data"]["low"],
            "platform": "bitforex"
        }    

    def normalize_balances(self):
        """Normalize balances data."""
        pass


class Public(object):
    """Public endpoints."""

    @classmethod
    def get_symbols(cls):
        """Get available trading symbols."""
        endpoint = "/api/v1/market/symbols"
        req = Request(base_url, endpoint)
        data = req.get()
        for i in data["data"]:
            yield i["symbol"]

    @classmethod
    def get_book(cls, symbol):
        endpoint = "/api/v1/market/depth?symbol={}&size=1".format(symbol)
        req = Request(base_url, endpoint)
        rsl = req.get()
        if "data" in rsl.keys():
            return rsl["data"]

    @classmethod
    def get_tickers(cls):
        """Fetch tickers from echange"""
        endpoint = "/api/v1/market/ticker?symbol=" # + pair e.g.: BCHBTC
        pair_list = cls.get_symbols()
        for pair in pair_list:
            req = Request(base_url, "{}{}".format(endpoint, pair))
            data = req.get()
            if data["success"] is True:
                parser = Normalizer({"symbol":pair, "data":data["data"]})
                normalized = parser.normalize_ticker()
                if normalized is not None:
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

    def create_signature(self, query):
        """
            Create signature to authenticate requests.
            
            :param query
                Query to use in signature.
        """
        signature = hmac.new(
            bytearray(self.secret, "utf-8"), 
            query.encode("utf-8"),
            digestmod="SHA256"
            ).hexdigest()
        return signature

    def get_balances(self):
        # FIXME not working but why??
        """Get Balances from exchange"""
        nonce = int(time.time() * 1000)
        endpoint = "/api/v1/fund/allAccount"
        query = "{}?accessKey={}&nonce={}".format(endpoint, self.key, nonce)
        signature = self.create_signature(query)
        query_signed = "{}&signData={}".format(query, signature)
        req = Request(base_url, query_signed)
        rsl = req.post(headers=None)
        balances = []
        for i in rsl:
            if isinstance(i, dict):
                logging.info(i)
                balances.append({
                    "coin": i["currency"].upper(),
                    "balance": i["fix"]
                })
        if len(balances) > 0:
            return balances
        else: return rsl

    def cancel_order(self, order_id, symbol):
        """ 
            Cancel order.

            :param order_id
                Order id to be cancelled.
            :param cur
                Cur to use in market selection.
            :param coin
                Coin to use in market selection.
        """
        nonce = int(time.time()) * 1000
        endpoint = "/api/v1/trade/cancelOrder"
        query = "{}?accessKey={}&orderId={}&symbol={}&nonce={}".format(
            endpoint, self.key, order_id, symbol, nonce
        )
        signature = self.create_signature(query)
        query_signed = query + "&signData={}".format(signature)
        req = Request(base_url, query_signed)
        rsl = req.post(headers=None)
        if "error" in rsl.keys():
            logging.error("Error {} in {}".format(rsl.__dict__, __name__.upper()))
            return rsl
        return rsl

    def create_order(self, cur, coin, amount, price, dir):
        # FIXME returns invalid signData.
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

        if dir == "buy":
            dir = 1
        elif dir == "sell":
            dir = 2
        symbol = "coin-{}-{}".format(cur.lower(), coin.lower())
        nonce = int(time.time()) * 1000
        endpoint = "/api/v1/trade/placeOrder"
        query = "{}?accessKey={}&amount={}&price={}&symbol={}&tradeType={}&nonce={}".format(
            endpoint, self.key, amount, price, symbol, dir, nonce
            )
        logging.info(query)
        signature = self.create_signature(query)
        query_signed = "{}&signData={}".format(query, signature)
        req = Request(base_url, query_signed)
        rsl = req.post(headers=None)
        if rsl["success"] == True:
            time.sleep(5)
            self.cancel_order(rsl, symbol)
        return rsl["message"]


def create_order(key, secret, cur, coin, amount, price, dir):
    return Private(key,secret).create_order(cur, coin, amount, price, dir)
    
   
def get_balances(key, secret):
    return Private(key, secret).get_balances()


def get_tickers():
    return Public.get_tickers()

def run():
    #for backwards compatibility
    return Public.get_tickers()