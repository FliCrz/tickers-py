#!/bin/env python
import os
import time
import logging
import json
import hmac
import requests

from libs import Request


# for ease api_docs_url = https://docs.bitfinex.com/docs

base_url = "https://api-pub.bitfinex.com"
api_auth_url = "https://api.bitfinex.com"


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
        for e in self.raw_data:
            try:
                yield {
                    "symbol": e,
                    "cur": e[3:],
                    "coin": e[:3]
                }
            except Exception as e:
                logging.error("Error normalizing_symbols {} in {}".format(
                    e, __name__.upper()
                ))
                pass

    def normalize_ticker(self, *symbols_dict):
        """
            Normalize ticker data for the upcoming model.

            :param symbols_dict
                Dictionary of symbols to confirm cur, coin.
        """
        symbol = self.raw_data[0].split("t")[1]
        cur = symbol[int(len(symbol) / 2):]
        coin = symbol[:int(len(symbol) / 2)]
        return {
            "cur": cur.upper(),
            "coin": coin.upper(),
            "last_price": self.raw_data[7],
            "buy": self.raw_data[1],
            "buy_amount": self.raw_data[2],
            "sell": self.raw_data[3],
            "sell_amount": self.raw_data[4],
            "high": self.raw_data[9],
            "low": self.raw_data[10],
            "platform": "bitfinex"
        }

        
    def normalize_balances(self):
        """Normalize balances data."""
        pass


class Public(object):
    """Public endpoints."""

    @classmethod
    def get_symbols(cls):
        """
            Get trading symbols from exchange.
        """
        endpoint = "/v2/conf/pub:list:pair:exchange"
        req = Request(base_url, endpoint)
        try:
            rsl = req.get()
            for e in rsl:
                parser = Normalizer(e)
                return parser.normalize_symbols()
        except Exception as e:
            logging.error("Error get_symbols {} in {}".format(
                e, __name__.upper()
            ))

    @classmethod
    def get_tickers(cls, *symbols_dict):
        """
            Fetch tickers from echange.
                        
            :param symbols_dict
            A Dict of symbols with following keys:
                - symbol
                - cur
                - coin
            Can be ommited.
        """
        endpoint = "/v2/tickers?symbols=ALL"
        req = Request(base_url, endpoint)
        try:
            data = req.get()
            for i in data:
                if i[0][0] == "t" and ":" not in i[0]: # Remove funding and derivatives ticker
                    parser = Normalizer(i)
                    parser = parser.normalize_ticker()
                    yield parser
        except Exception as e:
            logging.error("Error {} in {}".format(e, __name__.upper()))
            return e


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

    
    def create_signature_headers(self, endpoint, data=None):
        """
            Create signed headers for authentificated endpoints.

            :param: key
                API key to be used.
            :param secret
                API secret to be used.
            :param endpoint
                API endpoint targeted.
            :param data
                Data to be passed as request body.
        """
        # FIXME not  returning the correct key.
        nonce = int(time.time() * 1000) 
        if not data:
            signature = "/api{}{}".format(endpoint, nonce)
        else: 
            signature = "/api{}{}{}".format(endpoint, nonce, json.dumps(data))
        sig = hmac.new(
            bytearray(self.secret, "utf-8"), 
            signature.encode("utf-8"), 
            digestmod="SHA384"
            ).hexdigest()
        headers = {
            "bfx-nonce": str(nonce),
            "bfx-apikey": self.key,
            "bfx-signature": sig
        }
        return headers


    def get_balances(self):
        """Get Balances from exchange. Only exchange account is supported."""
        endpoint = "/v2/auth/r/wallets"
        headers = self.create_signature_headers(endpoint)
        req = Request(api_auth_url, endpoint)
        rsl = req.post(headers)
        balances = []
        for e in rsl:
            if e[0] == "exchange":
                balances.append({
                    "coin": e[1].upper(),
                    "balance": e[2]
                })
        return balances


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
        endpoint = "/v2/auth/w/order/submit"
        if dir == "sell":
            amount = float(amount) * -1

        data = {
            "type": "IOC",
            "symbol": "t{}{}".format(coin, cur),
            "price": price,
            "amount": amount
        }
        headers = self.create_signature_headers(endpoint, data)
        req = Request(api_auth_url, endpoint)
        rsl = req.post(headers, data)
        if len(rsl) >= 7:
            return rsl[7]
        logging.info(rsl)
        return rsl[2]


def create_order(key, secret, cur, coin, amount, price, dir):
    return Private(key,secret).create_order(cur, coin, amount, price, dir)
    
   
def get_balances(key, secret):
    return Private(key, secret).get_balances()


def get_tickers():
    return Public.get_tickers()

def run():
    #for backwards compatibility
    return Public.get_tickers()