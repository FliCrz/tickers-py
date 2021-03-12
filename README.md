# Exchange Wrappers
This is a python app to get a standardized output from the supported exchanges 
api. <br>
It can either be used via the command line or by spinning up either a simple python 
server or a full set of services with background fetching and saving to a redis 
instance. Both can be queried but the simple server needs to have data saved manually
via the command line.

## How to use?

### Command Line
Get all available commands with: <br>
`python3 main.py --help`<br>

```
exchange_wrappers
author: ko.ktk@pm.me

python3 main.py <command> <options>

commands:
-h, --help                           this help screen.
-e, --exchanges <filename>           get available exchanges.
                                     optionally provide the exchanges filename.
-t, --tickers [exchange name]        get current tickers for some exchange.
-t [exchange name] <currency> <coin> optionally you can pass a currency and coin symbols (in that order).
-c, --coins [symbol]                 get a list of supported coins from our information provider (coinpaprika).
                                     optionally you can pass the coin symbol to get its id.
-i, --info [coin id]                 get coin information, you need to supply the coin-id, use -c with symbol to get it.
-l, --log [level]                    get logging with level.
-R, --server                         run flask server and use it as api.
                                     WARNING: if possible use the docker-compose.yml to spin up all services.
                                     app will be reachable at address http://localhost:5000.
```

### WebServer
You can either spin up a python flask server with: <br>
`cd src` <br>
`python3 main.py -R` or `python3 main.py --server` <br>
<br>
Available routes are: <br>
```
/get_exchanges/<all | active>
/get_coin/<all | symbol>
/get_ticker/<all | exchange_name>
```