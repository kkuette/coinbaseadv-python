# cbadv/WebsocketClient.py
# original author: Daniel Paquin
#
#
# Template object to receive messages from the Coinbase Websocket Feed

from __future__ import print_function
import json, time, hmac, hashlib
from threading import Thread
from websocket import create_connection, WebSocketConnectionClosedException
from cbadv.cbadv_auth import get_auth_headers


class WebsocketClient(object):
    def __init__(
            self,
            api_key,
            api_secret,
            url="wss://advanced-trade-ws.coinbase.com",
            products=None,
            message_type="subscribe",
            should_print=True,
            # Make channels a required keyword-only argument; see pep3102
            *,
            # Channel options: status, ticker, ticker_batch, level2, user, market_trades
            channel):
        self.url = url
        self.products = products
        self.channel = channel
        self.type = message_type
        self.stop = True
        self.error = None
        self.ws = None
        self.thread = None
        self.api_key = api_key
        self.api_secret = api_secret
        self.should_print = should_print

    def start(self):
        def _go():
            self._connect()
            self._listen()
            self._disconnect()

        self.stop = False
        self.on_open()
        self.thread = Thread(target=_go)
        self.keepalive = Thread(target=self._keepalive)
        self.thread.start()

    def _connect(self):
        if self.products is None:
            self.products = ["BTC-USD"]
        elif not isinstance(self.products, list):
            self.products = [self.products]

        if self.url[-1] == "/":
            self.url = self.url[:-1]

        if self.channel is None:
            self.channel = "ticker"
            sub_params = {'type': 'subscribe', 'channel': self.channel, 'product_ids': self.products}
        else:
            sub_params = {'type': 'subscribe', 'channel': self.channel, 'product_ids': self.products}

        timestamp = str(int(time.time()))
        message = timestamp + ''.join(self.channel) + ','.join(self.products)
        auth_headers = get_auth_headers(timestamp, message, self.api_key, self.api_secret)
        sub_params['signature'] = auth_headers['CB-ACCESS-SIGN']
        sub_params['api_key'] = auth_headers['CB-ACCESS-KEY']
        sub_params['timestamp'] = auth_headers['CB-ACCESS-TIMESTAMP']

        self.ws = create_connection(self.url)
        self.ws.send(json.dumps(sub_params))

    def _keepalive(self, interval=30):
        while self.ws.connected:
            self.ws.ping("keepalive")
            time.sleep(interval)

    def _listen(self):
        self.keepalive.start()
        while not self.stop:
            try:
                data = self.ws.recv()
                msg = json.loads(data)
            except ValueError as e:
                self.on_error(e)
            except Exception as e:
                self.on_error(e)
                self._reconnect()
            else:
                self.on_message(msg)

    def _disconnect(self):
        try:
            if self.ws:
                self.ws.close()
        except WebSocketConnectionClosedException as e:
            pass
        finally:
            self.keepalive.join()

        self.on_close()

    def _reconnect(self):
        self._disconnect()
        time.sleep(0.01)  # Wait for 0.01 seconds before reconnecting
        self._connect()
        self._listen()

    def close(self):
        self.stop = True   # will only disconnect after next msg recv
        self._disconnect() # force disconnect so threads can join
        self.thread.join()

    def on_open(self):
        if self.should_print:
            print("-- Subscribed! --\n")

    def on_close(self):
        if self.should_print:
            print("\n-- Socket Closed --")
        self._reconnect()

    def on_message(self, msg):
        if self.should_print:
            print(msg)

    def on_error(self, e, data=None):
        self.error = e
        self.stop = True
        print('{} - data: {}'.format(e, data))


if __name__ == "__main__":
    import sys, json, time
    import cbadv

    conf_path = 'conf.json'

    class MyWebsocketClient(cbadv.WebsocketClient):
        def __init__(self, channel, **kwargs):
            super().__init__(channel=channel, **kwargs)

        def on_open(self):
            self.url = "wss://advanced-trade-ws.coinbase.com"
            self.products = ["BTC-USD"]
            self.message_count = 0
            print("Let's count the messages!")

        def on_message(self, msg):
            print(json.dumps(msg, indent=4, sort_keys=True))
            self.message_count += 1

        def on_close(self):
            print("-- Goodbye! --")

    wsClient = MyWebsocketClient(channel="level2", **json.load(open(conf_path)))
    wsClient.start()
    print(wsClient.url, wsClient.products)
    try:
        while True:
            print("\nMessageCount =", "%i \n" % wsClient.message_count)
            time.sleep(1)
    except KeyboardInterrupt:
        wsClient.close()

    if wsClient.error:
        sys.exit(1)
    else:
        sys.exit(0)
