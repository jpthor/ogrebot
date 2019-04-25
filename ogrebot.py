from pyogre import api
import json
import time
import six
import logging
import random
import requests


logger = logging.getLogger("ogredump")
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


class ogrebot(object):

    def __init__(self, sfile="settings.json"):
        try:
            with open(sfile) as f:
                self.settings = json.load(f)
        except Exception:
            raise Exception("Settings file is not a proper json file")

        self.api = api(self.settings.get("apikey"), self.settings.get("apisecret"))
        logger.info("ogrebot started")
        self.minsize = 0.0001
        self.hour = int(0)

#######
    def iterbalances(self, skipzero=True):
        # yields: symbolname, available balance, junk balance, ordered balance, ask price
        for symbol, balance in six.iteritems(self.api.balances()["balances"]):
            if symbol == "BTC":
                yield "BTC", balance, 0, 0, 1.0, "hodl"
            else:
                if skipzero and not balance:
                    continue
                ask, strategy = self.get_askstrategy(symbol)
                if not ask:
                    continue
                if balance and ask:
                    abalance = self.api.balance(symbol)["available"]
                    size = abalance * ask
                    if size < self.minsize:
                        jbalance = abalance
                        abalance = 0
                    else:
                        jbalance = 0
                else:
                    abalance = 0
                    jbalance = 0
                obalance = balance - abalance - jbalance
                yield symbol, abalance, jbalance, obalance, ask, strategy

    def iterbtcbalances(self):
        for symbol, abalance, jbalance, obalance, ask, _ in self.iterbalances():
            if symbol == "BTC":
                obtc = obalance
            else:
                orders = self.api.myorders("BTC-%s" % symbol)
                obtc = 0
                for order in orders:
                    if order["type"] == "sell":
                        obtc += order["price"] * order["quantity"]
            yield symbol, abalance * ask, jbalance * ask, obtc

    def get_askstrategy(self, symbol):
        market = "BTC-%s" % symbol
        strategy = self.settings.get("strategies", {}).get(market, "hodl").lower()
        orders = self.api.orders(market)
        if len(orders["buy"]):
            maxbuy = max(orders["buy"])
        else:
            maxbuy = None
        if len(orders["sell"]):
            minsell = min(orders["sell"].keys())
        else:
            minsell = None

        if strategy == "selltake":
            ask = maxbuy
        elif strategy == "sellmake":
            ask = minsell
        elif strategy == "sellmakelow":
            if (minsell - 1e-8) > maxbuy:
                ask = minsell - 1e-8
            else:
                ask = maxbuy
        elif strategy == "hodl":
            ask = maxbuy
            # check your volume on over all volume
        return ask, strategy

##### Trade
    def trade(self):
        for symbol, abalance, _jbalance, _obalance, ask, strategy in self.iterbalances():
            if symbol == "BTC" or strategy == "hodl":
                continue
            if abalance:
                sellSize = self.settings.get("sellDaily")
                sellSize = int(sellSize)/int(24)
                abalance = (sellSize/2) + random.randint(1,sellSize)
                size = abalance * ask
                market = "BTC-%s" % symbol
                logger.info("EXECUTING ORDER: AMOUNT: %s%s, PRICE %.8fBTC: SIZE:%.8fBTC" % (
                    abalance, symbol, ask, size))

                order = self.api.sellorder(market, abalance, ask)

                if order["success"]:
                    uuid = order["uuid"]
                    if uuid:
                        logger.info("ORDER PLACED SUCCESSFULLY: UUID: %s" % order["uuid"])
                    else:
                        logger.info("ORDER SOLD SUCCESSFULLY: AMOUNT: %sBTC" % size)
                else:
                    logger.warning("ORDER FAILED: %s" % order.get("error"))

##### tx
    def tx(self):
        # Decimals for the chain precision
        decimals = int(1000000000)
        txSize = int(self.settings.get("sellDaily"))

        cyclesDay = int(86400)/int(self.settings.get("cycleTime"))
        print("cyclesDay: %s" % cyclesDay)

        if self.hour == cyclesDay:
            print("hour = %s" % self.hour)

            # simple wallet is running on the localhost and port of 18082
            url = "http://localhost:18082/json_rpc"

            # standard json header
            headers = {'content-type': 'application/json'}
            destination_address = self.settings.get("destaddr")
            int_amount =  txSize * decimals

            # send specified LOK amount to the given destination_address
            recipients = [{"address": destination_address, "amount": int_amount}]

            # simplewallet' procedure/method to call
            rpc_input = {"method": "transfer", "params": {"destinations": recipients, "priority" : 0}}

            # add standard rpc values
            rpc_input.update({"jsonrpc": "2.0", "id": "0"})

            # execute the rpc request
            response = requests.post(url, data=json.dumps(rpc_input), headers=headers)

            logger.info("SENDING TX: AMOUNT: %s" % (int_amount/decimals))

            self.hour = 0

            # order = json.loads(response.json())
            # logger.info("TX Hash %s" % order['tx_hash'])

        else:
            self.hour = self.hour + 1
            print("hour = %s" % self.hour)

##### time
    def time(self):
        cycle = int(self.settings.get("cycleTime"))
        print("cycle %s" % cycle)
        time.sleep(cycle)

if __name__ == "__main__":
    bot = ogrebot()
    while True:
        bot.trade()
        bot.tx()
        bot.time()
