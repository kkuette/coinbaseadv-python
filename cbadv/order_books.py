# cbadv/order_books.py
# original author: Tony Denion
#
#
# Live order books updated from the Coinbase Advanced Trade Websocket Feed

import pickle

from cbadv.websocket_client import WebsocketClient
from cbadv.order_book import OrderBook

class OrderBooks(WebsocketClient):

    def __init__(self, product_id=["BTC-USD"], log_to=None):
        super(OrderBooks, self).__init__(
            products=product_id, channels=['full'])
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
            order_book.sequence = -1
        print("-- Subscribed to OrderBooks! --\n")

    def on_close(self):
        print("\n-- OrderBook Socket Closed! --")

    def on_message(self, msg):
        if msg['type'] != 'subscriptions':
            if self._log_to:
                pickle.dump(msg, self._log_to)
            self.order_books[msg['product_id']]._message(msg)

if __name__ == '__main__':
    import sys
    import time
    import datetime as dt

    class OrderBooksConsole(OrderBooks):
        ''' Logs real-time changes to the bid-ask spread to the console '''

        def __init__(self, product_id=None):
            super(OrderBooksConsole, self).__init__(product_id=product_id)

            # latest values of bid-ask spread for each product
            self._bid = {}
            self._ask = {}
            self._bid_depth = {}
            self._ask_depth = {}

        def on_message(self, message):
            if message['type'] != 'subscriptions':
                super(OrderBooksConsole, self).on_message(message)

                # Calculate newest bid-ask spread
                bid = self.order_books[message['product_id']].get_bid()
                bids = self.order_books[message['product_id']].get_bids(bid)
                bid_depth = sum([b['size'] for b in bids])
                ask = self.order_books[message['product_id']].get_ask()
                asks = self.order_books[message['product_id']].get_asks(ask)
                ask_depth = sum([a['size'] for a in asks])

                # Log changes to the bid-ask spread to the console
                if bid != self._bid[message['product_id']] or ask != self._ask[message['product_id']]:
                    self._bid[message['product_id']] = bid
                    self._ask[message['product_id']] = ask
                    self._bid_depth[message['product_id']] = bid_depth
                    self._ask_depth[message['product_id']] = ask_depth
                    print('{} {} bid: {:.3f} @ {:.2f}\task: {:.3f} @ {:.2f}'.format(
                        dt.datetime.now(), message['product_id'], bid_depth, bid, ask_depth, ask))

    order_books = OrderBooksConsole(product_id=['BTC-USD', 'ETH-USD'])
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