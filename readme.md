OgreBot is a bot to liquidate daily Monero miner earnings to BTC on TradeOgre.
The bot interfaces with Monero-RPC.

The bot sends an on-chain transaction to your TradeOgre destination address every day, then makes a trade every time period that is defined (in seconds).

**MoneroSetup**

1) MoneroD running in a screen
```
cd monero
screen <enter>
./monerod
```

2) MoneroRPC running in a screen
```
cd monero
screen <enter>
./monero-wallet-rpc --wallet-file ****** --password "********" --rpc-bind-port 18082 --disable-rpc-login
```

**Installation:**
On the third screen clone and install six (python compatibility library)
```
screen <enter>
git clone
sudo easy_install six
```

Requires a python wrapper to interface with TradeOgre APIs.
```
sudo python setup.py install
```

Settings are stored in the settings.json file.

Edit settings json with your:
- TradeOgre apikey
- TradeOrgre apisecret
- TradeOgre Monero Destination Address
- Amount to sell every day
- Cycle period (seconds - recommend 3600 for 1 hour)
- Trade strategy (default is "selltake"):
1) "sellmake": Asset will be sold with the lowest price in the available sell-orders
2) "sellmakelow": Asset will be sold with lowest price -1 satoshi
3) "selltake": Asset will be sold with the highest buy orders available

**Start Bot**

Start the python bot:
```
python ogrebot.py
```

Exit all screens safely using:
```
ctrl-ad
```


Use `Trade_Ogre_Bot` on telegram to monitor assets
