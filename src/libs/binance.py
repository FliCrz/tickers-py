import hmac, time
import logging
from libs import Request
from urllib.parse import urlencode


# for ease api_docs_url = https://binance-docs.github.io/apidocs/spot/en/#system-status-system


base_url = "https://api.binance.com"


class Normalizer(object):
    """
        Data normalizer.
    """
    def __init__(self, raw_data):
        self.raw_data = raw_data

    def normalize_symbols(self):
        """ Normalize symbols data result."""
        for e in self.raw_data["symbols"]:
            try:
                yield {
                    "symbol": e["symbol"],
                    "cur": e["quoteAsset"],
                    "coin": e["baseAsset"]
                }
            except Exception as e:
                logging.error("Error normalizing_symbols {} in {}".format(
                    e, __name__.upper()
                ))
                pass

    def normalize_ticker(self, symbols_dict):
        """
            Normalize ticker data for the upcoming model.

            :param symbols_dict
                Dictionary of symbols to confirm cur, coin.
        """
        for i in symbols_dict:
            if i["symbol"] == self.raw_data["symbol"]:
                cur = i["cur"]
                coin = i["coin"]
                return {
                    "cur": cur.upper(),
                    "coin": coin.upper(),
                    "last_price": 0,
                    "buy": self.raw_data["bidPrice"],
                    "buy_amount": self.raw_data["bidQty"],
                    "sell": self.raw_data["askPrice"],
                    "sell_amount": self.raw_data["askQty"],
                    "high": 0,
                    "low": 0,
                    "platform": "binance"
                }
 
    def normalize_balances(self):
        """Normalize balances. Only spot account supported"""
        balances = []
        for b in self.raw_data["balances"]:
            try:
                balances.append({
                    "coin": b["asset"].upper(),
                    "balance": float(b["free"]) + float(b["locked"])
                    })
            except Exception as e:
                logging.error("Error normalizing_balances {} in {}".format(
                    e, __name__.upper()
                ))
                pass
        return balances
        

class Public(object):
    """
        Public API endpoints.
    """
    @classmethod
    def get_symbols(cls):
        """
            Retrieve available symbols. Useful for filtering.
        """
        endpoint = "/api/v3/exchangeInfo"
        req = Request(base_url, endpoint)
        try:
            rsl = req.get()
            parser = Normalizer(rsl)
            return parser.normalize_symbols()
        except Exception as e:
            logging.error("Error {} in {}".format(e, __name__.upper()))
            return e


    @classmethod
    def get_tickers(cls, *symbols_dict):
        """
            Retrieve ticker form Exchange.

            :param symbols_dict
                A Dict of symbols with following keys:
                    - symbol
                    - cur
                    - coin
                Can be ommited.
        """
        if not symbols_dict:
            symbols_dict = Public.get_symbols()
        endpoint = "/api/v3/ticker/bookTicker"
        req = Request(base_url, endpoint)
        try:
            rsl = req.get()
            for i in rsl:
                parser = Normalizer(i)
                yield parser.normalize_ticker(symbols_dict)
        except Exception as e:
            logging.error("Error {} in {}".format(e, __name__.upper()))
            return e
        

class Private(object):
    """
        Private API endpoints.
    """

    def __init__(self, key, secret):
        self.key = key
        self.secret = secret
    
    def create_signature(self, query):
        """
            Create signature for authentificated endpoints.

            :param query
                Query dict to be url encoded.
        """
        return  hmac.new(
            bytearray(self.secret, "utf-8"), 
            urlencode(query).encode("utf-8"), 
            digestmod="SHA256"
            ).hexdigest()

    def get_balances(self):
        """
            Get user balances. Only spot account supported.
        """
        endpoint = "/api/v3/account"
        query = {
            "timestamp": int(round(time.time() * 1000))
        }
        signature = self.create_signature(query)
        headers = {
            "X-MBX-APIKEY": self.key
        }
        query["signature"] = signature
        try:
            req = Request(base_url, endpoint)
            rsl = req.get(headers, query)
            parser = Normalizer(rsl)
            return parser.normalize_balances()
        except Exception as e:
            logging.error("Error: {} in {}".format(e, __name__.upper()))
            return e

    def create_order(self, cur, coin, amount, price, dir):
        """
            Create order. Only spot account supported.

            :param cur
                Currency to use to create the order.
            :param coin
                Coin to use to create the order.
            :param amount
                Amount to use to create the order. 
                TODO Should check if within user balance else use user balance.
            :param price
                Not used, kept for compatibility with other wrappers.
            :param dir
                Direction of the order. Needs to be one of "buy" or "sell".
        """ 
        if dir.lower() not in ["buy", "sell"]:
            return None
        if None in [cur, coin, amount]:
            return None
        endpoint = "/api/v3/order"
        symbol = coin + cur
        query = {
            "side": dir.upper(),
            "symbol": symbol.upper(),
            "timestamp": int(time.time() * 1000),
            "type": "MARKET",
            "quantity": float(amount)
        }
        headers = {
            "X-MBX-APIKEY": self.key
        }
        signature = self.create_signature(query)
        query["signature"] = signature
        req = Request(base_url, endpoint)
        try:
            rsl = req.post(headers, query)
            logging.error(rsl)
            return rsl
        except Exception as e:
            logging.error("Error {} in {}".format(e, __name__.upper()))
            return e


def create_order(key, secret, cur, coin, amount, price, dir):
    return Private(key,secret).create_order(cur, coin, amount, price, dir)


def get_balances(key, secret):
    return Private(key, secret).get_balances()


def get_tickers():
    return Public.get_tickers()

def run():
    #for backwards compatibility
    return Public.get_tickers()