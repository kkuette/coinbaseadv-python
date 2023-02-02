# cbadv/order_book.py
# original author: David Caseria
#
#
# Live order book updated from the Coinbase Websocket Feed

from sortedcontainers import SortedDict
from decimal import Decimal

from cbadv.cbadv_client import Client

class OrderBook:
    def __init__(self, product_id='BTC-USD'):
        self._asks = SortedDict()
        self._bids = SortedDict()
        self.product = product_id
        self._client = Client()
        self._sequence = 0
        self._current_ticker = None

    def _message(self, events):
        if self._sequence == 0:
            self.create_book(events)
        else:
            self.update(events)

    def create_book(self, events):
        self._asks = SortedDict()
        self._bids = SortedDict()
        for event in events:
            event = self.type_event(event)
            if event['side'] == 'bid':
                self._bids[event['price_level']] = event
            else:
                self._asks[event['price_level']] = event
        self._sequence += 1

    def update(self, events):
        for event in events:
            event = self.type_event(event)
            if event['new_quantity'] == 0:
                self.remove(event)
            else:
                if event['side'] == 'bid':
                    self._bids[event['price_level']] = event
                else:
                    self._asks[event['price_level']] = event
        self._sequence += 1

    def remove(self, event):
        if event['side'] == 'bid':
            if event['price_level'] in self._bids:
                del self._bids[event['price_level']]
        else:
            if event['price_level'] in self._asks:
                del self._asks[event['price_level']]

    def type_event(self, event):
        event['price_level'] = Decimal(event['price_level'])
        event['new_quantity'] = Decimal(event['new_quantity'])
        return event


    def get_ask(self):
        return self._asks.peekitem(0)[1]

    def get_bid(self):
        return self._bids.peekitem(-1)[1]
