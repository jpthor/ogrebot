import json
import requests
import six
from requests.auth import HTTPBasicAuth


class api(object):
    def __init__(self, key=None, secret=None):
        self.key = key
        self.secret = secret
        if self.key and self.secret:
            self.auth = HTTPBasicAuth(self.key, self.secret)
        else:
            self.auth = None

    def __query(self, path, auth, method, **kwargs):
        if auth:
            auth = self.auth
            if auth is None:
                raise Exception("%s path needs authentication" % path)
        r = requests.request(method, 'https://tradeogre.com/api/v1' + path,
                             auth=HTTPBasicAuth(self.key, self.secret), data=kwargs)
        return json.loads(r.text)

    @staticmethod
    def __objectify(d):
        # this method fixes broken json data types in reponse data
        # ie: float values returning strings etc..
        if isinstance(d, dict):
            ret = {}
            for x, y in six.iteritems(d):
                if isinstance(y, six.string_types) and \
                        (y.isdigit() or y.replace(".", "").isdigit()):
                    y = float(y)
                if isinstance(x, six.string_types) and \
                        (x.isdigit() or x.replace(".", "").isdigit()):
                    x = float(x)
                ret[x] = y
        elif isinstance(d, six.string_types):
            if d.lower() == "true":
                ret = True
            elif d.lower() == "false":
                ret = False
            else:
                ret = d
        else:
            ret = d
        return ret

    @staticmethod
    def __stringify(d):
        if isinstance(d, (int, float)):
            return "%.8f" % d

    def markets(self):
        markets = self.__query("/markets", False, "get")
        return [{x: self.__objectify(y) for x, y in six.iteritems(z)} for z in markets]

    def orders(self, market):
        orders = self.__query("/orders/%s" % market, False, "get")
        for k in ["sell", "buy"]:
            if k not in orders or not len(orders[k]):
                orders[k] = {}
        return {x: self.__objectify(y) for x, y in six.iteritems(orders)}

    def ticker(self, market):
        return self.__objectify(self.__query("/ticker/%s" % market, False, "get"))

    def history(self, market):
        return [self.__objectify(x) for x in self.__query("/history/%s" % market, False, "get")]

    def buyorder(self, market, quantity, price):
        quantity = self.__stringify(quantity)
        price = self.__stringify(price)
        return self.__objectify(self.__query("/order/buy", True, "post", market=market,
                                             quantity=quantity, price=price))

    def sellorder(self, market, quantity, price):
        quantity = self.__stringify(quantity)
        price = self.__stringify(price)
        return self.__objectify(self.__query("/order/sell", True, "post", market=market,
                                             quantity=quantity, price=price))

    def cancelorder(self, uuid):
        return self.__query("/order/cancel", True, "post", uuid=uuid)

    def myorders(self, market=None):
        if market:
            kwargs = {"market": market}
        else:
            kwargs = {}
        return [self.__objectify(x) for x in self.__query("/account/orders", True,
                                                          "post", **kwargs)]

    def myorder(self, uuid):
        return self.__objectify(self.__query("/account/order/%s" % uuid, True, "get"))

    def balance(self, currency):
        return self.__objectify(self.__query("/account/balance", True, "post", currency=currency))

    def balances(self):
        balances = self.__query("/account/balances", True, "get")
        balances["balances"] = self.__objectify(balances["balances"])
        return balances
