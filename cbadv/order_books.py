# cbadv/order_books.py
# original author: Tony Denion
#
#
# Live order books updated from the Coinbase Advanced Trade Websocket Feed

import pickle

from cbadv.websocket_client import WebsocketClient
from cbadv.order_book import OrderBook

class OrderBooks(WebsocketClient):

    def __init__(self, api_key, api_secret, product_id=["BTC-USD", "ETH-USD"], log_to=None):
        super(OrderBooks, self).__init__(api_key, api_secret, 
            products=product_id, channel='level2')
        self.product_id = product_id
        self.order_books = {}
        self._log_to = log_to
        if self._log_to:
            assert hasattr(self._log_to, 'write')
        self.init_order_books()

    def init_order_books(self):
        for product_id in self.product_id:
            self.order_books[product_id] = OrderBook(product_id=product_id)
        
    def on_open(self):
        for order_book in self.order_books.values():
            order_book.sequence = 0
        print("-- Subscribed to OrderBooks! --\n")

    def on_close(self):
        print("\n-- OrderBook Socket Closed! --")

    def on_message(self, msg):
        if self._log_to:
            pickle.dump(msg, self._log_to)
        for event in msg['events']:
            if not 'subscriptions' in event:
                    self.order_books[event['product_id']]._message(event['updates'])


if __name__ == '__main__':
    import sys, json
    import time
    import datetime as dt

    class OrderBooksConsole(OrderBooks):
        ''' Logs real-time changes to the bid-ask spread to the console '''

        def __init__(self, api_key, api_secret, product_id=None):
            super(OrderBooksConsole, self).__init__(api_key, api_secret, product_id=product_id)
            self._bid = {}
            self._ask = {}
            self._bid_depth = {}
            self._ask_depth = {}

            for product_id in self.product_id:
                # Initialize the bid-ask spread for each product
                self._bid[product_id] = 0
                self._ask[product_id] = 0
                self._bid_depth[product_id] = 0
                self._ask_depth[product_id] = 0

        def on_message(self, message):
            super(OrderBooksConsole, self).on_message(message)

            for event in message['events']:
                if not 'subscriptions' in event:
                    # Calculate newest bid-ask spread
                    bid = self.order_books[event['product_id']].get_bid()['price_level']
                    bid_depth = self.order_books[event['product_id']].get_bid()['new_quantity']
                    ask = self.order_books[event['product_id']].get_ask()['price_level']
                    ask_depth = self.order_books[event['product_id']].get_ask()['new_quantity']

                    # Log changes to the bid-ask spread to the console
                    if bid != self._bid[event['product_id']] or ask != self._ask[event['product_id']] or \
                        bid_depth != self._bid_depth[event['product_id']] or ask_depth != self._ask_depth[event['product_id']]:
                        self._bid[event['product_id']] = bid
                        self._ask[event['product_id']] = ask
                        self._bid_depth[event['product_id']] = bid_depth
                        self._ask_depth[event['product_id']] = ask_depth
                        print('{} {} bid: {} @ {:.2f}\task: {} @ {:.2f}'.format(
                            dt.datetime.now(), event['product_id'], bid_depth, bid, ask_depth, ask))

    conf_path = 'conf.json'

    order_books = OrderBooksConsole(product_id=['BTC-USD', 'ETH-USD'], **json.load(open(conf_path)))
    order_books.start()
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        order_books.close()

    if order_books.error:
        sys.exit(1)
    else:
        sys.exit(0)